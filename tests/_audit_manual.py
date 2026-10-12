"""
Manual audit script — run once to check all routes with auth.
Not part of the formal test suite.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ['FLASK_ENV'] = 'testing'

from app import create_app
from werkzeug.security import generate_password_hash

app = create_app('development')

with app.test_client() as client:
    with app.app_context():
        from models.database import execute_db, query_db
        try:
            uid = execute_db(
                'INSERT INTO users (username,email,password_hash,education_level) VALUES (?,?,?,?)',
                ['_audit_user', '_audit@test.local', generate_password_hash('TestPass1!'), 'undergraduate']
            )
            execute_db('INSERT INTO student_profiles (user_id) VALUES (?)', [uid])
        except Exception:
            u = query_db('SELECT id FROM users WHERE username=?', ['_audit_user'], one=True)
            uid = u['id'] if u else None

    resp = client.post('/login', data={'identifier': '_audit_user', 'password': 'TestPass1!'})
    print(f'POST /login: {resp.status_code} Location={resp.headers.get("Location")}')

    routes = [
        '/dashboard', '/recommend', '/skills', '/roadmap',
        '/projects', '/resume', '/interview', '/profile',
        '/careers', '/careers/software_developer',
        '/api/careers', '/api/roadmap/software_developer',
    ]
    for r in routes:
        resp = client.get(r)
        print(f'GET {r}: {resp.status_code}')

    # POST tests
    post_tests = [
        ('/recommend', {
            'education_level': 'undergraduate', 'degree_course': 'CS',
            'interests': 'programming', 'technical_skills': 'Python, SQL',
            'soft_skills': 'communication', 'experience_level': 'beginner',
            'preferred_field': 'technology', 'career_goals': 'build software',
        }),
        ('/skills', {'career': 'software_developer',
                     'skill_Python': 'intermediate', 'skill_JavaScript': 'basic',
                     'skill_Git': 'advanced', 'skill_SQL': 'intermediate',
                     'skill_Data_Structures': 'not_learned', 'skill_Algorithms': 'not_learned',
                     'skill_OOP': 'intermediate', 'skill_REST_APIs': 'basic'}),
        ('/roadmap', {'career': 'software_developer', 'completed_steps': ['1', '2']}),
        ('/projects', {'action': 'save', 'project_key': 'expense_tracker', 'status': 'planned'}),
        ('/resume', {
            'name': 'Test User', 'email': 'test@test.com', 'phone': '123',
            'location': 'City', 'summary': 'A developer.',
            'education': 'BSc CS', 'technical_skills': 'Python',
            'soft_skills': 'Communication', 'projects': 'Test app',
            'certifications': '', 'experience': '', 'achievements': '',
        }),
        ('/interview', {'action': 'get_questions', 'career_role': 'Software Developer',
                        'topic': 'python', 'difficulty': 'beginner'}),
        ('/interview/feedback', {'question': 'What is Python?', 'answer': 'Python is a programming language.',
                                 'career_role': 'Software Developer', 'topic': 'python', 'difficulty': 'beginner'}),
        ('/profile', {
            'degree_course': 'CS', 'interests': 'coding',
            'technical_skills': 'Python', 'soft_skills': 'communication',
            'experience_level': 'beginner', 'preferred_field': 'technology',
            'career_goals': 'build apps',
        }),
    ]
    for url, data in post_tests:
        r2 = client.post(url, data=data)
        print(f'POST {url}: {r2.status_code} Location={r2.headers.get("Location")}')

print('\nDone.')
