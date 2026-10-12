"""
Resume assistance service.
Generates structured resume drafts from user-provided data.
Never invents degrees, certifications, or experience.
"""

from typing import Dict


def build_resume(data: Dict) -> str:
    """
    Build a plain-text resume draft from user-provided fields.
    Returns structured text suitable for display and PDF export.
    All content is sourced directly from the user's input.
    """
    name = data.get('name', 'Your Name').strip()
    email = data.get('email', '').strip()
    phone = data.get('phone', '').strip()
    location = data.get('location', '').strip()
    summary = data.get('summary', '').strip()
    education = data.get('education', '').strip()
    technical_skills = data.get('technical_skills', '').strip()
    soft_skills = data.get('soft_skills', '').strip()
    projects = data.get('projects', '').strip()
    certifications = data.get('certifications', '').strip()
    experience = data.get('experience', '').strip()
    achievements = data.get('achievements', '').strip()

    lines = []

    # Header
    lines.append(name.upper())
    contact_parts = [p for p in [email, phone, location] if p]
    if contact_parts:
        lines.append(' | '.join(contact_parts))
    lines.append('─' * 60)

    # Summary
    if summary:
        lines.append('\nPROFESSIONAL SUMMARY')
        lines.append('─' * 20)
        lines.append(summary)

    # Education
    if education:
        lines.append('\nEDUCATION')
        lines.append('─' * 20)
        lines.append(education)

    # Technical Skills
    if technical_skills:
        lines.append('\nTECHNICAL SKILLS')
        lines.append('─' * 20)
        lines.append(technical_skills)

    # Soft Skills
    if soft_skills:
        lines.append('\nSOFT SKILLS')
        lines.append('─' * 20)
        lines.append(soft_skills)

    # Experience
    if experience:
        lines.append('\nEXPERIENCE')
        lines.append('─' * 20)
        lines.append(experience)

    # Projects
    if projects:
        lines.append('\nPROJECTS')
        lines.append('─' * 20)
        lines.append(projects)

    # Certifications
    if certifications:
        lines.append('\nCERTIFICATIONS')
        lines.append('─' * 20)
        lines.append(certifications)

    # Achievements
    if achievements:
        lines.append('\nACHIEVEMENTS')
        lines.append('─' * 20)
        lines.append(achievements)

    return '\n'.join(lines)


def get_resume_tips() -> Dict:
    """Return structured resume writing tips."""
    return {
        'summary': 'Write 2–3 sentences summarising your strongest skills, education, and career goal. Be specific and confident.',
        'education': 'List your most recent qualification first. Include institution name, degree, subject, and expected or actual graduation year.',
        'technical_skills': 'List specific tools, languages, and frameworks you have used. Group them by category (e.g. Languages: Python, JavaScript; Databases: MySQL, SQLite).',
        'soft_skills': 'Mention skills such as communication, teamwork, or problem-solving — ideally supported by examples.',
        'projects': 'Describe each project in one or two sentences. Include the technologies used and the outcome or purpose.',
        'certifications': 'List certifications with the issuing organisation and year (e.g. Google IT Support Certificate — Coursera, 2024).',
        'experience': 'Use action verbs (developed, built, analysed, managed). Include the organisation, role, and dates if available.',
        'achievements': 'Quantify achievements where possible (e.g. Improved page load speed by 40% through code optimisation).',
    }
