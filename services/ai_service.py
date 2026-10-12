"""
AI service layer.
Wraps the configured AI API (e.g. OpenAI-compatible).
Falls back to rule-based demo responses when credentials are absent.
API keys are never exposed to the frontend.
"""

import os
import json
import urllib.request
import urllib.error
from typing import Optional


def _api_request(messages: list, max_tokens: int = 800) -> Optional[str]:
    """Send a chat completion request to the configured API endpoint."""
    api_key = os.environ.get('AI_API_KEY', '')
    api_url = os.environ.get('AI_API_URL', 'https://api.openai.com/v1/chat/completions')
    model = os.environ.get('AI_MODEL', 'gpt-3.5-turbo')

    if not api_key:
        return None

    payload = json.dumps({
        'model': model,
        'messages': messages,
        'max_tokens': max_tokens,
        'temperature': 0.7,
    }).encode('utf-8')

    req = urllib.request.Request(
        api_url,
        data=payload,
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}',
        },
        method='POST',
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            return data['choices'][0]['message']['content'].strip()
    except (urllib.error.URLError, KeyError, json.JSONDecodeError):
        return None


# ──────────────────────────────────────────────────────────
# Public AI helper functions
# Each function has a rule-based fallback used in demo mode.
# ──────────────────────────────────────────────────────────

def enhance_career_explanation(career_title: str, match_reasons: list, profile: dict) -> str:
    """Return a personalised explanation of why a career may suit the user."""
    messages = [
        {
            'role': 'system',
            'content': (
                'You are a helpful career guidance advisor. '
                'Provide a concise, encouraging 2–3 sentence explanation of why a career may suit a student. '
                'Do not guarantee employment or success. Be honest and supportive.'
            ),
        },
        {
            'role': 'user',
            'content': (
                f"Career: {career_title}\n"
                f"Matching reasons: {'; '.join(match_reasons)}\n"
                f"Student interests: {profile.get('interests', 'not specified')}\n"
                f"Student skills: {profile.get('technical_skills', 'not specified')}\n"
                "Explain in 2–3 sentences why this career may be a good fit."
            ),
        },
    ]
    result = _api_request(messages, max_tokens=200)
    if result:
        return result

    # Fallback
    reasons_text = '; '.join(match_reasons[:2]) if match_reasons else 'general interest alignment'
    return (
        f"Based on your profile, {career_title} appears to be a strong match. "
        f"{reasons_text}. "
        f"With the right preparation and learning, this career path can offer meaningful and rewarding opportunities."
    )


def generate_interview_feedback(question: str, answer: str, role: str) -> dict:
    """Generate structured feedback for an interview answer."""
    messages = [
        {
            'role': 'system',
            'content': (
                'You are an experienced technical interviewer providing constructive feedback. '
                'Respond ONLY with a valid JSON object with keys: '
                '"strengths" (string), "missing_points" (string), '
                '"improvement_suggestions" (string), "sample_answer" (string). '
                'Be constructive and encouraging. Clearly label sample answers as examples only.'
            ),
        },
        {
            'role': 'user',
            'content': (
                f"Interview role: {role}\n"
                f"Question: {question}\n"
                f"Candidate answer: {answer}\n"
                "Provide structured feedback."
            ),
        },
    ]
    result = _api_request(messages, max_tokens=600)
    if result:
        try:
            # Extract JSON if wrapped in markdown code fences
            if '```' in result:
                result = result.split('```')[1]
                if result.startswith('json'):
                    result = result[4:]
            return json.loads(result)
        except (json.JSONDecodeError, IndexError):
            pass

    # Fallback demo feedback
    return _demo_interview_feedback(question, answer, role)


def _demo_interview_feedback(question: str, answer: str, role: str) -> dict:
    """Rule-based demo feedback when AI API is unavailable."""
    word_count = len(answer.split()) if answer else 0
    if word_count < 20:
        quality = "brief"
        strengths = "Your answer shows initial understanding of the topic."
        missing = "Your answer would benefit from more detail, specific examples, and technical depth."
        suggestions = "Try to expand your answer with concrete examples from your experience or studies. Use the STAR method (Situation, Task, Action, Result) where applicable."
    elif word_count < 60:
        quality = "moderate"
        strengths = "You have provided a reasonable answer that covers some important points."
        missing = "Consider adding specific technical details, examples, or quantifiable outcomes."
        suggestions = "Strengthen your answer by mentioning specific tools, technologies, or methodologies you have used or studied."
    else:
        quality = "detailed"
        strengths = "Your answer is detailed and demonstrates good understanding of the topic."
        missing = "Review whether you have addressed all aspects of the question clearly."
        suggestions = "Ensure your answer is well-structured. Consider summarising key points at the end."

    sample = (
        f"[Sample answer for learning purposes] A strong answer to this {role} question would typically include: "
        f"a clear explanation of the concept, a practical example demonstrating application, "
        f"any relevant tools or methodologies, and a brief summary of outcomes or lessons learned."
    )
    return {
        'strengths': strengths,
        'missing_points': missing,
        'improvement_suggestions': suggestions,
        'sample_answer': sample,
    }


def improve_resume_section(section: str, content: str) -> str:
    """Suggest improvements to a resume section."""
    messages = [
        {
            'role': 'system',
            'content': (
                'You are a professional resume editor. '
                'Improve the clarity, professionalism, and impact of the provided resume content. '
                'Do not invent degrees, certifications, or experience. '
                'Return only the improved text.'
            ),
        },
        {
            'role': 'user',
            'content': f"Resume section: {section}\nContent: {content}\nPlease improve this content.",
        },
    ]
    result = _api_request(messages, max_tokens=300)
    if result:
        return result
    return content  # Return original if API unavailable
