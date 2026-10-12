"""
Career recommendation engine.

Uses rule-based weighted scoring against structured career data in data/careers.json.
All logic is self-contained — no AI API dependency.

Scoring dimensions (max points each):
  FIELD_MATCH      30  Preferred field / category alignment
  SKILL_OVERLAP    40  Technical skill overlap (up to 8 skills × 5 pts)
  KEYWORD_MATCH    20  Keyword hits in user profile text (up to 4 hits × 5 pts)
  SOFT_SKILLS      10  Soft skill overlap (up to 5 × 2 pts)

  Max raw = 100.  Score is normalised to 0–100 and labelled:
    80–100  Strong match
    60–79   Good match
    40–59   Possible match
    0–39    Exploratory
"""

import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Career data — loaded once at module level
# ---------------------------------------------------------------------------

_CAREER_DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'careers.json')


def _load_careers() -> List[Dict]:
    with open(_CAREER_DATA_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


CAREERS: List[Dict] = _load_careers()
CAREER_MAP: Dict[str, Dict] = {c['key']: c for c in CAREERS}

# ---------------------------------------------------------------------------
# Scoring weights
# ---------------------------------------------------------------------------

_W_FIELD   = 30
_W_SKILL   = 40   # up to 8 matched skills × 5
_W_KW      = 20   # up to 4 keyword hits × 5
_W_SOFT    = 10   # up to 5 soft skill hits × 2
_MAX_RAW   = _W_FIELD + _W_SKILL + _W_KW + _W_SOFT  # 100

# Confidence thresholds (applied to 0-100 normalised score)
_CONFIDENCE_THRESHOLDS = [
    (80, 'Strong Match'),
    (60, 'Good Match'),
    (40, 'Possible Match'),
    (0,  'Exploratory'),
]

# Learning resource suggestions keyed by skill name fragment
_SKILL_RESOURCES: Dict[str, str] = {
    'python':          'freeCodeCamp Python Course / Python.org docs',
    'javascript':      'freeCodeCamp JavaScript Course / javascript.info',
    'sql':             'SQLZoo / Mode Analytics SQL Tutorial',
    'html':            'freeCodeCamp Responsive Web Design / MDN Web Docs',
    'css':             'CSS Tricks / Flexbox Froggy',
    'git':             'Pro Git Book (free) / GitHub Learning Lab',
    'machine learning':'fast.ai / Google Machine Learning Crash Course',
    'deep learning':   'fast.ai Deep Learning / Coursera Deep Learning Specialisation',
    'data visualis':   'Storytelling with Data (book) / Tableau Public tutorials',
    'statistics':      'Khan Academy Statistics / StatQuest YouTube',
    'react':           'React official docs / Scrimba React Course',
    'figma':           'Figma official tutorials / DesignCourse YouTube',
    'ui':              'Google UX Design Certificate (Coursera)',
    'ux':              'Google UX Design Certificate (Coursera)',
    'cybersecurity':   'TryHackMe / CompTIA Security+ Study Materials',
    'networking':      'Professor Messer (CompTIA Network+) / Cisco NetAcad',
    'cloud':           'AWS / Azure / GCP free tier + official learning paths',
    'linux':           'Linux Foundation free courses / OverTheWire Wargames',
    'seo':             'Google Search Central Documentation',
    'marketing':       'HubSpot Academy / Google Digital Garage',
    'excel':           'Microsoft Excel for Beginners (GCFLearnFree)',
    'pandas':          'Pandas official docs / Kaggle Pandas course',
    'tensorflow':      'TensorFlow official tutorials',
    'pytorch':         'PyTorch official tutorials',
    'docker':          'Docker official docs / TechWorld with Nana YouTube',
    'kubernetes':      'Kubernetes official docs / KodeKloud',
    'rest api':        'RESTful API Design (book) / Postman learning centre',
    'oop':             'Object-Oriented Programming in Python (Real Python)',
}


# ---------------------------------------------------------------------------
# Input validation
# ---------------------------------------------------------------------------

_FIELD_MAX_LEN: Dict[str, int] = {
    'education_level':  50,
    'degree_course':   120,
    'interests':       500,
    'technical_skills': 500,
    'soft_skills':     300,
    'experience_level': 50,
    'preferred_field':  50,
    'career_goals':    600,
}

_ALLOWED_EDUCATION_LEVELS = {
    'secondary', 'diploma', 'undergraduate',
    'postgraduate', 'graduate', '',
}

_ALLOWED_EXPERIENCE_LEVELS = {'beginner', 'intermediate', 'experienced', ''}

_ALLOWED_FIELDS = {
    'technology', 'data', 'design', 'security', 'marketing',
    'business', 'cloud', '',
}


def validate_profile(raw: Dict) -> Tuple[Dict, List[str]]:
    """
    Sanitise and validate a raw profile dict from form input.

    Returns:
        (cleaned_profile, error_list)
        error_list is empty when the profile is valid.

    Cleaning:
      - Strip leading/trailing whitespace from all string values.
      - Truncate fields that exceed their maximum allowed length.
      - Validate enumerated fields against allowed sets.
    """
    errors: List[str] = []
    cleaned: Dict = {}

    for field, max_len in _FIELD_MAX_LEN.items():
        raw_val = raw.get(field, '')
        if not isinstance(raw_val, str):
            raw_val = str(raw_val)
        val = raw_val.strip()
        if len(val) > max_len:
            errors.append(
                f"'{field}' is too long (max {max_len} characters). "
                f"The value has been trimmed for processing."
            )
            val = val[:max_len]
        cleaned[field] = val

    # Validate enumerations
    edu = cleaned.get('education_level', '').lower()
    if edu and edu not in _ALLOWED_EDUCATION_LEVELS:
        errors.append(
            f"Unrecognised education level '{edu}'. "
            "Please select from the provided options."
        )
        cleaned['education_level'] = ''

    exp = cleaned.get('experience_level', '').lower()
    if exp and exp not in _ALLOWED_EXPERIENCE_LEVELS:
        errors.append(
            f"Unrecognised experience level '{exp}'. "
            "Defaulting to 'beginner'."
        )
        cleaned['experience_level'] = 'beginner'

    field_pref = cleaned.get('preferred_field', '').lower()
    if field_pref and field_pref not in _ALLOWED_FIELDS:
        errors.append(
            f"Unrecognised preferred field '{field_pref}'. "
            "It has been treated as open."
        )
        cleaned['preferred_field'] = ''

    return cleaned, errors


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _whole_word(keyword: str, text: str) -> bool:
    """Return True if *keyword* appears as a whole word in *text*."""
    # Build a pattern that respects word boundaries but also handles
    # multi-word keywords (e.g. "machine learning").
    escaped = re.escape(keyword)
    pattern = r'(?<![a-z0-9])' + escaped + r'(?![a-z0-9])'
    return bool(re.search(pattern, text, re.IGNORECASE))


def _parse_skill_list(raw: str) -> List[str]:
    """Split a comma-separated skill string into a cleaned list."""
    return [s.strip().lower() for s in raw.split(',') if s.strip()]


def _skill_overlap(user_skills: List[str], career_skills: List[str]) -> Tuple[List[str], List[str]]:
    """
    Return (matched, gaps) by fuzzy substring comparison.
    A career skill matches if any user skill is a substring of it or vice versa.
    """
    matched = []
    gaps = []
    for cs in career_skills:
        cs_lower = cs.lower()
        if any(us in cs_lower or cs_lower in us for us in user_skills):
            matched.append(cs)
        else:
            gaps.append(cs)
    return matched, gaps


def _confidence_label(score: int) -> str:
    for threshold, label in _CONFIDENCE_THRESHOLDS:
        if score >= threshold:
            return label
    return 'Exploratory'


# ---------------------------------------------------------------------------
# Learning suggestions
# ---------------------------------------------------------------------------

def get_learning_suggestions(career_key: str, skill_gaps: List[str]) -> List[Dict]:
    """
    Return ordered learning suggestions for the given skill gaps.

    Each item:
        { 'skill': str, 'resource': str, 'estimated_hours': str }

    Skills that have no specific resource entry get a generic suggestion.
    """
    career = CAREER_MAP.get(career_key)
    learning_topics = career.get('learning_topics', []) if career else []

    suggestions = []
    for skill in skill_gaps:
        skill_lower = skill.lower()
        resource = 'Search for beginner tutorials and official documentation.'
        for key, res in _SKILL_RESOURCES.items():
            if key in skill_lower or skill_lower in key:
                resource = res
                break

        # Very rough hour estimate: 10 hrs per skill (clearly labelled as suggestion)
        suggestions.append({
            'skill':            skill,
            'resource':         resource,
            'estimated_hours':  '~10–20 hours (suggested)',
        })

    # Append any learning_topics from the career that are not already listed
    gap_lower = {s.lower() for s in skill_gaps}
    for topic in learning_topics:
        if topic.lower() not in gap_lower and not any(
            topic.lower() in s or s in topic.lower() for s in gap_lower
        ):
            resource = 'Search for beginner tutorials and official documentation.'
            for key, res in _SKILL_RESOURCES.items():
                if key in topic.lower() or topic.lower() in key:
                    resource = res
                    break
            suggestions.append({
                'skill':           topic,
                'resource':        resource,
                'estimated_hours': '~10–20 hours (suggested)',
            })

    return suggestions


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_all_careers() -> List[Dict]:
    return CAREERS


def get_career(key: str) -> Optional[Dict]:
    return CAREER_MAP.get(key)


def get_careers_by_category(category: str) -> List[Dict]:
    return [c for c in CAREERS if c['category'] == category]


def get_skill_gap(career_key: str, user_skills: List[str]) -> Dict:
    """
    Compare user's skills against a career's requirements.

    Returns:
        {
            'career':               dict,
            'required_skills':      list,
            'matched_skills':       list,
            'skill_gaps':           list,
            'completion_percentage': int,
        }
    """
    career = get_career(career_key)
    if not career:
        return {}

    user_skills_lower = [s.strip().lower() for s in user_skills if s.strip()]
    required = career.get('required_skills', [])
    matched, gaps = _skill_overlap(user_skills_lower, required)

    return {
        'career':               career,
        'required_skills':      required,
        'matched_skills':       matched,
        'skill_gaps':           gaps,
        'completion_percentage': round(len(matched) / len(required) * 100) if required else 0,
    }


def recommend_careers(profile: Dict) -> List[Dict]:
    """
    Rule-based career matching against data/careers.json.

    Accepts raw (un-validated) profile dicts — validation is applied internally.

    Profile keys used:
        education_level, degree_course, interests, technical_skills,
        soft_skills, experience_level, preferred_field, career_goals

    Returns up to 5 results, each containing:
        {
            'career':              dict,           # full career object
            'match_score':         int,            # 0–100 normalised
            'confidence':          str,            # Strong / Good / Possible / Exploratory
            'match_reasons':       list[str],      # human-readable explanations
            'match_breakdown':     list[dict],     # per-dimension scores
            'matched_skills':      list[str],      # skills user already has
            'skill_gaps':          list[str],      # skills to develop
            'learning_suggestions':list[dict],     # ordered study suggestions
            'is_fallback':         bool,           # True for exploratory padding
        }

    Disclaimer: Results are for guidance only and do not guarantee employment
    or predict career success.
    """
    cleaned, _errors = validate_profile(profile)

    interests_raw   = cleaned.get('interests', '').lower()
    tech_raw        = cleaned.get('technical_skills', '').lower()
    soft_raw        = cleaned.get('soft_skills', '').lower()
    preferred_field = cleaned.get('preferred_field', '').lower()
    goals_raw       = cleaned.get('career_goals', '').lower()

    # Combined profile text for keyword scanning
    profile_text = ' '.join([interests_raw, tech_raw, soft_raw, goals_raw])

    user_tech_skills  = _parse_skill_list(tech_raw)
    user_soft_skills  = _parse_skill_list(soft_raw)

    results = []

    for career in CAREERS:
        field_pts = 0
        skill_pts = 0
        kw_pts    = 0
        soft_pts  = 0
        reasons   = []
        breakdown = []

        # ── 1. Preferred field / category match ────────────────────────
        cat = career['category'].lower()
        title_lower = career['title'].lower()
        if preferred_field and (
            preferred_field in cat or
            cat in preferred_field or
            title_lower in preferred_field
        ):
            field_pts = _W_FIELD
            reasons.append(
                f"Matches your preferred field ({preferred_field.title()})."
            )

        breakdown.append({
            'dimension': 'Field Alignment',
            'points':    field_pts,
            'max':       _W_FIELD,
            'detail':    f"Preferred field: '{preferred_field or 'open'}', career category: '{cat}'",
        })

        # ── 2. Technical skill overlap ──────────────────────────────────
        career_required = career.get('required_skills', [])
        matched_skills, skill_gaps = _skill_overlap(user_tech_skills, career_required)

        if matched_skills:
            # 5 pts per matched skill, capped at _W_SKILL
            skill_pts = min(len(matched_skills) * 5, _W_SKILL)
            reasons.append(
                f"You already have {len(matched_skills)} relevant skill(s): "
                f"{', '.join(matched_skills[:4])}{'…' if len(matched_skills) > 4 else ''}."
            )

        breakdown.append({
            'dimension': 'Skill Overlap',
            'points':    skill_pts,
            'max':       _W_SKILL,
            'detail':    f"{len(matched_skills)}/{len(career_required)} required skills matched",
        })

        # ── 3. Keyword matching (whole-word) ────────────────────────────
        kw_hits = [
            kw for kw in career.get('keywords', [])
            if _whole_word(kw, profile_text)
        ]
        if kw_hits:
            kw_pts = min(len(kw_hits) * 5, _W_KW)
            reasons.append(
                f"Your profile mentions: {', '.join(kw_hits[:4])}{'…' if len(kw_hits) > 4 else ''}."
            )

        breakdown.append({
            'dimension': 'Keyword Relevance',
            'points':    kw_pts,
            'max':       _W_KW,
            'detail':    f"{len(kw_hits)} keyword hit(s): {', '.join(kw_hits[:4]) or 'none'}",
        })

        # ── 4. Soft skills ──────────────────────────────────────────────
        career_soft = [s.lower() for s in career.get('soft_skills', [])]
        soft_matched = [
            s for s in career_soft
            if any(us in s or s in us for us in user_soft_skills)
        ]
        if soft_matched:
            soft_pts = min(len(soft_matched) * 2, _W_SOFT)

        breakdown.append({
            'dimension': 'Soft Skills',
            'points':    soft_pts,
            'max':       _W_SOFT,
            'detail':    f"{len(soft_matched)} soft skill(s) matched",
        })

        raw_score = field_pts + skill_pts + kw_pts + soft_pts

        if raw_score > 0:
            # Normalise to 0–100
            normalised = round((raw_score / _MAX_RAW) * 100)
            normalised = max(1, min(normalised, 100))

            if not reasons:
                reasons.append(
                    'This career may align with your general interests and goals.'
                )

            learning_sugg = get_learning_suggestions(career['key'], skill_gaps)

            results.append({
                'career':               career,
                'match_score':          normalised,
                'confidence':           _confidence_label(normalised),
                'match_reasons':        reasons,
                'match_breakdown':      breakdown,
                'matched_skills':       matched_skills,
                'skill_gaps':           skill_gaps,
                'learning_suggestions': learning_sugg,
                'is_fallback':          False,
            })

    # Sort descending by score
    results.sort(key=lambda x: x['match_score'], reverse=True)
    results = results[:5]

    # ── Pad to minimum 3 with exploratory suggestions ───────────────────
    if len(results) < 3:
        added_keys = {r['career']['key'] for r in results}
        for career in CAREERS:
            if career['key'] in added_keys:
                continue
            if len(results) >= 5:
                break

            career_required = career.get('required_skills', [])
            matched_skills, skill_gaps = _skill_overlap(user_tech_skills, career_required)
            learning_sugg = get_learning_suggestions(career['key'], skill_gaps)

            results.append({
                'career':               career,
                'match_score':          5,
                'confidence':           'Exploratory',
                'match_reasons':        [
                    'This is a popular career path worth exploring, '
                    'even if it did not closely match your current profile.'
                ],
                'match_breakdown':      [],
                'matched_skills':       matched_skills,
                'skill_gaps':           skill_gaps,
                'learning_suggestions': learning_sugg,
                'is_fallback':          True,
            })

    return results[:5]
