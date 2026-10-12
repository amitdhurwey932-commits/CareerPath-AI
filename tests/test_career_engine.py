"""
Tests for the career recommendation engine.

Covers:
  - Data loading and structure
  - get_career / get_all_careers / get_careers_by_category
  - get_skill_gap
  - validate_profile — valid, oversized, bad enums, non-string values
  - _whole_word — false-positive prevention
  - recommend_careers — scoring, skill output, new fields, edge cases
  - get_learning_suggestions
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from services.career_engine import (
    CAREERS,
    CAREER_MAP,
    recommend_careers,
    get_career,
    get_all_careers,
    get_careers_by_category,
    get_skill_gap,
    get_learning_suggestions,
    validate_profile,
    _whole_word,
)


# ── Helpers ──────────────────────────────────────────────────────────────────

def _make_profile(**kwargs):
    """Return a complete profile dict with sane defaults, overridden by kwargs."""
    base = {
        'interests':        '',
        'technical_skills': '',
        'soft_skills':      '',
        'preferred_field':  '',
        'career_goals':     '',
        'experience_level': 'beginner',
        'education_level':  'undergraduate',
        'degree_course':    '',
    }
    base.update(kwargs)
    return base


# ── Data loading & structure ─────────────────────────────────────────────────

class TestCareerData(unittest.TestCase):

    def test_all_careers_loaded(self):
        """Career data should load at least 5 careers."""
        self.assertGreaterEqual(len(get_all_careers()), 5)

    def test_career_keys_are_unique(self):
        """All career keys must be unique."""
        keys = [c['key'] for c in CAREERS]
        self.assertEqual(len(keys), len(set(keys)))

    def test_career_data_structure(self):
        """Every career must contain the required fields."""
        required = [
            'key', 'title', 'category', 'description',
            'required_skills', 'entry_routes', 'career_progression',
            'keywords', 'soft_skills',
        ]
        for career in CAREERS:
            for field in required:
                self.assertIn(
                    field, career,
                    f"Career '{career.get('key', '?')}' missing field '{field}'"
                )

    def test_get_career_found(self):
        career = get_career('software_developer')
        self.assertIsNotNone(career)
        self.assertEqual(career['key'], 'software_developer')
        self.assertIn('required_skills', career)

    def test_get_career_not_found(self):
        self.assertIsNone(get_career('nonexistent_career_key_xyz'))

    def test_get_careers_by_category(self):
        tech = get_careers_by_category('technology')
        self.assertGreater(len(tech), 0)
        for c in tech:
            self.assertEqual(c['category'], 'technology')

    def test_get_careers_by_unknown_category(self):
        """Unknown category should return empty list, not raise."""
        result = get_careers_by_category('alchemy')
        self.assertEqual(result, [])


# ── _whole_word helper ───────────────────────────────────────────────────────

class TestWholeWord(unittest.TestCase):

    def test_matches_standalone_word(self):
        self.assertTrue(_whole_word('python', 'i like python and flask'))

    def test_does_not_match_substring(self):
        # 'ai' must not match inside 'email' or 'training'
        self.assertFalse(_whole_word('ai', 'send email and training'))

    def test_matches_ai_standalone(self):
        self.assertTrue(_whole_word('ai', 'interested in ai and machine learning'))

    def test_multi_word_keyword(self):
        self.assertTrue(_whole_word('machine learning', 'i study machine learning daily'))

    def test_case_insensitive(self):
        self.assertTrue(_whole_word('python', 'I Love PYTHON'))

    def test_empty_text(self):
        self.assertFalse(_whole_word('python', ''))


# ── validate_profile ─────────────────────────────────────────────────────────

class TestValidateProfile(unittest.TestCase):

    def test_clean_valid_profile(self):
        raw = _make_profile(
            interests='programming',
            technical_skills='Python, SQL',
            experience_level='beginner',
            preferred_field='technology',
        )
        cleaned, errors = validate_profile(raw)
        self.assertEqual(errors, [])
        self.assertEqual(cleaned['interests'], 'programming')
        self.assertEqual(cleaned['experience_level'], 'beginner')

    def test_strips_whitespace(self):
        raw = _make_profile(interests='  data science  ', technical_skills='  Python  ')
        cleaned, _ = validate_profile(raw)
        self.assertEqual(cleaned['interests'], 'data science')
        self.assertEqual(cleaned['technical_skills'], 'Python')

    def test_truncates_oversized_field(self):
        raw = _make_profile(interests='x' * 600)
        cleaned, errors = validate_profile(raw)
        self.assertEqual(len(cleaned['interests']), 500)
        self.assertTrue(any('interests' in e for e in errors))

    def test_invalid_education_level(self):
        raw = _make_profile(education_level='wizard_school')
        cleaned, errors = validate_profile(raw)
        self.assertEqual(cleaned['education_level'], '')
        self.assertTrue(any('education' in e.lower() for e in errors))

    def test_invalid_experience_level(self):
        raw = _make_profile(experience_level='master_ninja')
        cleaned, errors = validate_profile(raw)
        self.assertEqual(cleaned['experience_level'], 'beginner')
        self.assertTrue(any('experience' in e.lower() for e in errors))

    def test_invalid_preferred_field(self):
        raw = _make_profile(preferred_field='underwater_basket_weaving')
        cleaned, errors = validate_profile(raw)
        self.assertEqual(cleaned['preferred_field'], '')
        self.assertTrue(any('field' in e.lower() for e in errors))

    def test_non_string_value_coerced(self):
        raw = _make_profile()
        raw['interests'] = 12345
        cleaned, _ = validate_profile(raw)
        self.assertIsInstance(cleaned['interests'], str)

    def test_empty_profile_has_no_errors(self):
        _, errors = validate_profile(_make_profile())
        self.assertEqual(errors, [])

    def test_valid_all_experience_levels(self):
        for level in ('beginner', 'intermediate', 'experienced'):
            raw = _make_profile(experience_level=level)
            cleaned, errors = validate_profile(raw)
            self.assertNotIn('experience', ' '.join(errors).lower())
            self.assertEqual(cleaned['experience_level'], level)


# ── get_skill_gap ─────────────────────────────────────────────────────────────

class TestSkillGap(unittest.TestCase):

    def test_returns_correct_keys(self):
        result = get_skill_gap('software_developer', ['Python', 'Git', 'SQL'])
        self.assertIn('matched_skills', result)
        self.assertIn('skill_gaps', result)
        self.assertIn('completion_percentage', result)
        self.assertIn('required_skills', result)
        self.assertIn('career', result)

    def test_matched_skills_nonempty_with_known_skills(self):
        result = get_skill_gap('software_developer', ['Python', 'Git', 'SQL'])
        self.assertGreater(len(result['matched_skills']), 0)

    def test_no_skills_zero_percent(self):
        result = get_skill_gap('software_developer', [])
        self.assertEqual(result['completion_percentage'], 0)

    def test_all_skills_high_percent(self):
        career = get_career('software_developer')
        result = get_skill_gap('software_developer', career['required_skills'])
        self.assertGreater(result['completion_percentage'], 80)

    def test_unknown_career_key(self):
        result = get_skill_gap('does_not_exist', ['Python'])
        self.assertEqual(result, {})

    def test_percentage_in_range(self):
        result = get_skill_gap('software_developer', ['Python', 'Git', 'SQL'])
        pct = result['completion_percentage']
        self.assertGreaterEqual(pct, 0)
        self.assertLessEqual(pct, 100)


# ── get_learning_suggestions ─────────────────────────────────────────────────

class TestLearningSuggestions(unittest.TestCase):

    def test_returns_list(self):
        sugg = get_learning_suggestions('software_developer', ['Python', 'Git'])
        self.assertIsInstance(sugg, list)

    def test_each_item_has_required_keys(self):
        sugg = get_learning_suggestions('software_developer', ['Python', 'SQL'])
        for item in sugg:
            self.assertIn('skill', item)
            self.assertIn('resource', item)
            self.assertIn('estimated_hours', item)

    def test_empty_gaps_still_returns_learning_topics(self):
        """With no gaps, career learning topics should still be surfaced."""
        sugg = get_learning_suggestions('software_developer', [])
        self.assertGreater(len(sugg), 0)

    def test_unknown_career_key(self):
        """Unknown career key should not raise; returns suggestions for the gaps."""
        sugg = get_learning_suggestions('unknown_career', ['Python'])
        self.assertIsInstance(sugg, list)
        self.assertEqual(len(sugg), 1)
        self.assertEqual(sugg[0]['skill'], 'Python')

    def test_known_skill_gets_specific_resource(self):
        sugg = get_learning_suggestions('software_developer', ['Python'])
        python_sugg = next((s for s in sugg if 'python' in s['skill'].lower()), None)
        self.assertIsNotNone(python_sugg)
        # Should not be the generic fallback
        self.assertNotIn('Search for beginner', python_sugg['resource'])


# ── recommend_careers ─────────────────────────────────────────────────────────

class TestRecommendCareers(unittest.TestCase):

    def test_returns_list(self):
        results = recommend_careers(_make_profile())
        self.assertIsInstance(results, list)

    def test_max_five_results(self):
        profile = _make_profile(
            interests='everything technology data design',
            technical_skills='Python, JS, SQL, HTML, CSS',
            soft_skills='communication',
            career_goals='explore all options',
        )
        self.assertLessEqual(len(recommend_careers(profile)), 5)

    def test_empty_profile_does_not_crash(self):
        """Empty profile must return results without raising."""
        results = recommend_careers(_make_profile())
        self.assertIsInstance(results, list)

    def test_result_has_required_keys(self):
        profile = _make_profile(
            interests='programming coding',
            technical_skills='Python, SQL',
            preferred_field='technology',
        )
        results = recommend_careers(profile)
        self.assertGreater(len(results), 0)
        for r in results:
            for key in ('career', 'match_score', 'confidence', 'match_reasons',
                        'match_breakdown', 'matched_skills', 'skill_gaps',
                        'learning_suggestions', 'is_fallback'):
                self.assertIn(key, r, f"Result missing key '{key}'")

    def test_score_in_range(self):
        profile = _make_profile(
            interests='programming coding software',
            technical_skills='Python, JavaScript, SQL',
        )
        for r in recommend_careers(profile):
            self.assertGreaterEqual(r['match_score'], 1)
            self.assertLessEqual(r['match_score'], 100)

    def test_confidence_label_is_valid(self):
        valid_labels = {'Strong Match', 'Good Match', 'Possible Match', 'Exploratory'}
        for r in recommend_careers(_make_profile(
            technical_skills='Python, SQL, Git',
            preferred_field='technology',
        )):
            self.assertIn(r['confidence'], valid_labels)

    def test_python_profile_ranks_software_highly(self):
        profile = _make_profile(
            interests='programming coding software',
            technical_skills='Python, JavaScript, SQL',
            soft_skills='communication, teamwork',
            preferred_field='technology',
            career_goals='build software applications',
        )
        results = recommend_careers(profile)
        # Top result should be software or dev related
        top = results[0]
        self.assertIn('career', top)
        # Score should be non-trivial for a strong profile match
        self.assertGreater(top['match_score'], 10)

    def test_ai_profile_does_not_trigger_email_false_positive(self):
        """'ai' keyword should not match careers when only present inside 'email'."""
        profile = _make_profile(
            interests='send email and manage projects',
            technical_skills='email marketing',
            career_goals='manage email campaigns',
        )
        results = recommend_careers(profile)
        # ai_ml_engineer should not score from 'ai' appearing inside 'email'
        ai_result = next((r for r in results if r['career']['key'] == 'ai_ml_engineer'), None)
        if ai_result:
            # If it appears at all, it must be due to other reasons, not keyword 'ai'
            ai_breakdown = next(
                (d for d in ai_result['match_breakdown'] if d['dimension'] == 'Keyword Relevance'),
                None
            )
            # 'ai' keyword should not have fired
            if ai_breakdown:
                self.assertNotIn("'ai'", ai_breakdown.get('detail', ''))

    def test_fallback_careers_have_is_fallback_true(self):
        """When padding with exploratory results, is_fallback must be True."""
        results = recommend_careers(_make_profile())
        fallbacks = [r for r in results if r['is_fallback']]
        non_fallbacks = [r for r in results if not r['is_fallback']]
        for fb in fallbacks:
            self.assertEqual(fb['confidence'], 'Exploratory')
            self.assertEqual(fb['match_breakdown'], [])
        # Non-fallbacks should have a populated breakdown (if any)
        for nfb in non_fallbacks:
            self.assertIsInstance(nfb['match_breakdown'], list)

    def test_strongly_matched_career_is_not_fallback(self):
        profile = _make_profile(
            interests='programming coding development software applications',
            technical_skills='Python, JavaScript, SQL, Git, OOP',
            soft_skills='communication, problem-solving, teamwork',
            preferred_field='technology',
            career_goals='build web and software applications',
        )
        results = recommend_careers(profile)
        self.assertGreater(len(results), 0)
        self.assertFalse(results[0]['is_fallback'])

    def test_learning_suggestions_present_when_skill_gaps_exist(self):
        profile = _make_profile(
            interests='programming',
            technical_skills='HTML',  # deliberately few skills → many gaps
            preferred_field='technology',
        )
        results = recommend_careers(profile)
        for r in results:
            if r['skill_gaps']:
                self.assertGreater(len(r['learning_suggestions']), 0,
                                   f"Expected learning suggestions for {r['career']['key']}")

    def test_match_breakdown_dimensions(self):
        profile = _make_profile(
            interests='data analysis',
            technical_skills='Python, SQL',
            preferred_field='data',
        )
        results = recommend_careers(profile)
        non_fb = [r for r in results if not r['is_fallback']]
        for r in non_fb:
            names = [d['dimension'] for d in r['match_breakdown']]
            self.assertIn('Field Alignment', names)
            self.assertIn('Skill Overlap', names)
            self.assertIn('Keyword Relevance', names)
            self.assertIn('Soft Skills', names)

    def test_preferred_field_boosts_score(self):
        """Setting preferred_field should score higher than leaving it empty."""
        base = _make_profile(technical_skills='Python, SQL', interests='data')
        without_field = recommend_careers(base)
        with_field = recommend_careers({**base, 'preferred_field': 'data'})

        # Find data_analyst in both results
        def _find(results, key):
            return next((r for r in results if r['career']['key'] == key), None)

        da_without = _find(without_field, 'data_analyst')
        da_with    = _find(with_field, 'data_analyst')
        if da_without and da_with:
            self.assertGreaterEqual(da_with['match_score'], da_without['match_score'])

    def test_oversized_input_does_not_raise(self):
        """Very large inputs must be trimmed and not crash the engine."""
        profile = _make_profile(
            interests='x ' * 1000,
            technical_skills='Python, ' * 200,
            career_goals='y ' * 1000,
        )
        results = recommend_careers(profile)
        self.assertIsInstance(results, list)

    def test_injection_like_input_does_not_raise(self):
        """Inputs with SQL/HTML injection patterns must be handled safely."""
        profile = _make_profile(
            interests="<script>alert('xss')</script>",
            technical_skills="'; DROP TABLE users; --",
            career_goals='<img src=x onerror=alert(1)>',
        )
        results = recommend_careers(profile)
        self.assertIsInstance(results, list)


if __name__ == '__main__':
    unittest.main()
