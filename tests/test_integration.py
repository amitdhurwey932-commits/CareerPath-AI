"""
Integration tests for CareerPath AI — full audit of routes, forms, DB operations.

Covers:
  - Registration: valid, duplicate, bad input
  - Login: valid, invalid, logout, access control
  - Dashboard: loads for logged-in user
  - Career recommendations: POST form saves to DB, results rendered
  - Skill assessment: POST saves skills, GET loads them back
  - Learning roadmap: progress saved and reloaded correctly
  - Project ideas: save, status update, remove
  - Resume assistant: generates draft, saves to DB
  - Interview: load questions, submit for feedback, topic/difficulty saved
  - Profile: update saved correctly
  - Admin: non-admin forbidden, admin allowed
  - Career explorer: list, detail, 404 for unknown
  - API endpoints: JSON responses
  - Access control: protected routes redirect when not logged in
"""

import sys
import os
import json
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from werkzeug.security import generate_password_hash

os.environ.setdefault('FLASK_ENV', 'testing')

# ── Isolated test database ────────────────────────────────────────────────────
# Use a dedicated temp file so tests never touch careerpath.db and never
# collide with data left over from previous runs.
_TEST_DB_FD, _TEST_DB_PATH = tempfile.mkstemp(suffix='_cpai_test.db')
os.close(_TEST_DB_FD)
os.environ['DATABASE_PATH'] = _TEST_DB_PATH

from app import create_app
from models.database import execute_db, query_db


# ── Fixture helpers ──────────────────────────────────────────────────────────

_COUNTER = [0]


def _unique(prefix: str) -> str:
    _COUNTER[0] += 1
    return f'{prefix}_{_COUNTER[0]}'


# Single shared app + app context for the whole module
_APP = None
_APP_CTX = None


def _get_app():
    global _APP, _APP_CTX
    if _APP is None:
        _APP = create_app('development')
        _APP.config['TESTING'] = True
        _APP_CTX = _APP.app_context()
        _APP_CTX.push()
    return _APP


class _BaseTest(unittest.TestCase):
    """
    Shared base class for integration tests.

    Each TEST METHOD gets a fresh client so session state never leaks between tests.
    Subclasses set _username in setUpClass; setUp() logs in before each test.
    """

    _username: str = ''
    _password: str = 'TestPass1!'

    @classmethod
    def setUpClass(cls):
        cls.app = _get_app()
        if not cls._username:
            cls._username = _unique('base')
        # Ensure the user exists in the DB
        with cls.app.app_context():
            existing = query_db(
                'SELECT id FROM users WHERE username=?', [cls._username], one=True
            )
            if not existing:
                uid = execute_db(
                    'INSERT INTO users (username,email,password_hash,education_level) VALUES (?,?,?,?)',
                    [cls._username, f'{cls._username}@test.local',
                     generate_password_hash(cls._password), 'undergraduate']
                )
                execute_db('INSERT INTO student_profiles (user_id) VALUES (?)', [uid])

    def setUp(self):
        """Each test gets its own client, pre-authenticated."""
        self.client = self.app.test_client()
        if self._username:
            self.client.post('/login', data={
                'identifier': self._username,
                'password': self._password,
            })

    def _register(self, username=None, password='TestPass1!', email=None, edu='undergraduate'):
        username = username or _unique('user')
        email = email or f'{username}@test.local'
        resp = self.client.post('/register', data={
            'username': username,
            'email': email,
            'password': password,
            'education_level': edu,
        }, follow_redirects=True)
        return username, email, resp

    def _login(self, username, password='TestPass1!'):
        return self.client.post('/login', data={
            'identifier': username,
            'password': password,
        }, follow_redirects=False)

    def _logout(self):
        self.client.get('/logout')


# ── Registration ─────────────────────────────────────────────────────────────

class TestRegistration(_BaseTest):
    """Registration tests always use an unauthenticated client."""

    @classmethod
    def setUpClass(cls):
        # Only initialise the app — do NOT create or log-in any user.
        cls.app = _get_app()

    def setUp(self):
        # Fresh unauthenticated client for every test.
        self.client = self.app.test_client()

    def test_register_valid_redirects_to_dashboard(self):
        username = _unique('regvalid')
        resp = self.client.post('/register', data={
            'username': username, 'email': f'{username}@test.local',
            'password': 'TestPass1!', 'education_level': 'undergraduate',
        })
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/dashboard', resp.headers['Location'])

    def test_register_duplicate_username_rejected(self):
        # Create user directly via DB, then try to register with same username
        username = _unique('regdup')
        with self.app.app_context():
            execute_db(
                'INSERT OR IGNORE INTO users (username,email,password_hash,education_level) VALUES (?,?,?,?)',
                [username, f'{username}@test.local',
                 generate_password_hash('TestPass1!'), 'undergraduate']
            )
        resp = self.client.post('/register', data={
            'username': username, 'email': f'{username}2@test.local',
            'password': 'TestPass1!', 'education_level': 'undergraduate',
        }, follow_redirects=True)
        self.assertIn(b'already registered', resp.data)

    def test_register_short_username_shows_error(self):
        resp = self.client.post('/register', data={
            'username': 'ab', 'email': _unique('ab') + '@test.local',
            'password': 'TestPass1!', 'education_level': 'undergraduate',
        }, follow_redirects=True)
        self.assertIn(b'at least 3', resp.data)

    def test_register_invalid_email_shows_error(self):
        resp = self.client.post('/register', data={
            'username': _unique('valid'), 'email': 'notanemail',
            'password': 'TestPass1!', 'education_level': 'undergraduate',
        }, follow_redirects=True)
        self.assertIn(b'valid email', resp.data)

    def test_register_short_password_shows_error(self):
        resp = self.client.post('/register', data={
            'username': _unique('valid2'), 'email': _unique('v2') + '@test.local',
            'password': 'short', 'education_level': 'undergraduate',
        }, follow_redirects=True)
        self.assertIn(b'at least 8', resp.data)

    def test_register_missing_education_shows_error(self):
        resp = self.client.post('/register', data={
            'username': _unique('noedu'), 'email': _unique('noedu') + '@test.local',
            'password': 'TestPass1!', 'education_level': '',
        }, follow_redirects=True)
        self.assertIn(b'education level', resp.data)

    def test_register_creates_student_profile(self):
        username = _unique('profilecreate')
        self.client.post('/register', data={
            'username': username, 'email': f'{username}@test.local',
            'password': 'TestPass1!', 'education_level': 'postgraduate',
        })
        with self.app.app_context():
            user = query_db('SELECT id FROM users WHERE username=?', [username], one=True)
            self.assertIsNotNone(user)
            profile = query_db('SELECT * FROM student_profiles WHERE user_id=?', [user['id']], one=True)
            self.assertIsNotNone(profile)


# ── Login / Logout / Access Control ─────────────────────────────────────────

class TestAuth(_BaseTest):
    _username = 'authtest_fixed'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.username = cls._username  # alias for test readability

    def test_login_valid(self):
        # Start fresh (setUp already logged us in); just verify session is active
        resp = self.client.get('/dashboard')
        self.assertEqual(resp.status_code, 200)

    def test_login_invalid_password(self):
        # Use a separate unauthenticated client
        c = self.app.test_client()
        resp = c.post('/login', data={
            'identifier': self._username,
            'password': 'WrongPassword!',
        })
        data = resp.data.decode('utf-8', errors='replace')
        self.assertIn('Invalid', data)
        self.assertEqual(resp.status_code, 200)

    def test_login_nonexistent_user(self):
        c = self.app.test_client()
        resp = c.post('/login', data={
            'identifier': 'nobody_at_all_xyz_999',
            'password': 'TestPass1!',
        })
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Invalid', resp.data)

    def test_logout_clears_session(self):
        self.client.get('/logout')
        resp = self.client.get('/dashboard')
        self.assertEqual(resp.status_code, 302)

    def test_protected_routes_redirect_when_not_logged_in(self):
        c = self.app.test_client()  # fresh unauthenticated client
        protected = ['/dashboard', '/recommend', '/skills', '/roadmap',
                     '/projects', '/resume', '/interview', '/profile']
        for route in protected:
            resp = c.get(route)
            self.assertEqual(resp.status_code, 302,
                             f'{route} should redirect unauthenticated users')

    def test_admin_forbidden_for_student(self):
        resp = self.client.get('/admin')
        self.assertEqual(resp.status_code, 403)

    def test_admin_accessible_for_admin(self):
        c = self.app.test_client()
        c.post('/login', data={'identifier': 'admin', 'password': 'Admin@1234'})
        resp = c.get('/admin')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Admin Dashboard', resp.data)


# ── Dashboard ────────────────────────────────────────────────────────────────

class TestDashboard(_BaseTest):
    _username = 'dashtest_fixed'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.username = cls._username

    def test_dashboard_loads(self):
        resp = self.client.get('/dashboard')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Welcome', resp.data)

    def test_dashboard_shows_username(self):
        resp = self.client.get('/dashboard')
        self.assertIn(self.username.encode(), resp.data)

    def test_dashboard_has_quick_actions(self):
        resp = self.client.get('/dashboard')
        data = resp.data.decode('utf-8', 'replace')
        self.assertIn('Career Recommendations', data)
        self.assertIn('Skill Assessment', data)
        self.assertIn('Learning Roadmap', data)


# ── Profile ──────────────────────────────────────────────────────────────────

class TestProfile(_BaseTest):
    _username = 'proftest_fixed'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.username = cls._username

    def test_profile_page_loads(self):
        resp = self.client.get('/profile')
        self.assertEqual(resp.status_code, 200)

    def test_profile_update_saves_to_db(self):
        resp = self.client.post('/profile', data={
            'degree_course': 'Computer Science',
            'interests': 'programming and data',
            'technical_skills': 'Python, SQL',
            'soft_skills': 'communication',
            'experience_level': 'intermediate',
            'preferred_field': 'technology',
            'career_goals': 'become a senior developer',
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Profile updated', resp.data)

        user = query_db('SELECT id FROM users WHERE username=?', [self.username], one=True)
        prof = query_db('SELECT * FROM student_profiles WHERE user_id=?', [user['id']], one=True)
        self.assertEqual(prof['degree_course'], 'Computer Science')
        self.assertEqual(prof['interests'], 'programming and data')
        self.assertEqual(prof['experience_level'], 'intermediate')


# ── Career Recommendations ───────────────────────────────────────────────────

class TestRecommend(_BaseTest):
    _username = 'rectest_fixed'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.username = cls._username

    def test_recommend_page_loads_get(self):
        resp = self.client.get('/recommend')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Career Recommendations', resp.data)

    def test_recommend_post_returns_results(self):
        resp = self.client.post('/recommend', data={
            'education_level': 'undergraduate',
            'degree_course': 'Computer Science',
            'interests': 'programming software development',
            'technical_skills': 'Python, JavaScript, SQL',
            'soft_skills': 'communication, teamwork',
            'experience_level': 'beginner',
            'preferred_field': 'technology',
            'career_goals': 'build web applications',
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.data.decode('utf-8', 'replace')
        self.assertIn('Career', data)
        self.assertIn('match', data)

    def test_recommend_post_saves_to_db(self):
        user = query_db('SELECT id FROM users WHERE username=?', [self.username], one=True)
        self.client.post('/recommend', data={
            'education_level': 'undergraduate',
            'degree_course': 'Computer Science',
            'interests': 'data analysis machine learning',
            'technical_skills': 'Python, SQL, Pandas',
            'soft_skills': 'analytical thinking',
            'experience_level': 'beginner',
            'preferred_field': 'data',
            'career_goals': 'work in data science',
        })
        recs = query_db(
            'SELECT * FROM career_recommendations WHERE user_id=?', [user['id']]
        )
        self.assertGreater(len(recs), 0)
        for rec in recs:
            self.assertIsNotNone(rec['career_key'])
            self.assertGreater(rec['match_score'], 0)

    def test_recommend_shows_guidance_disclaimer(self):
        resp = self.client.get('/recommend')
        self.assertIn(b'guidance only', resp.data)

    def test_recommend_validation_error_shown(self):
        resp = self.client.post('/recommend', data={
            'education_level': '',
            'degree_course': 'x' * 200,   # over limit
            'interests': '',
            'technical_skills': '',
            'soft_skills': '',
            'experience_level': 'beginner',
            'preferred_field': '',
            'career_goals': '',
        })
        self.assertEqual(resp.status_code, 200)
        # Should still return results (engine handles truncation internally)
        # Validation notices are displayed
        data = resp.data.decode('utf-8', 'replace')
        self.assertIn('Input notices', data)


# ── Skill Assessment ─────────────────────────────────────────────────────────

class TestSkillAssessment(_BaseTest):
    _username = 'skilltest_fixed'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.username = cls._username

    def test_skill_page_loads_without_career(self):
        resp = self.client.get('/skills')
        self.assertEqual(resp.status_code, 200)

    def test_skill_page_loads_with_career(self):
        resp = self.client.get('/skills?career=software_developer')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Software Developer', resp.data)

    def test_skill_post_saves_to_db(self):
        user = query_db('SELECT id FROM users WHERE username=?', [self.username], one=True)
        resp = self.client.post('/skills?career=software_developer', data={
            'career': 'software_developer',
            'skill_Python': 'intermediate',
            'skill_JavaScript': 'basic',
            'skill_Git': 'advanced',
            'skill_SQL': 'intermediate',
            'skill_Data_Structures': 'not_learned',
            'skill_Algorithms': 'not_learned',
            'skill_OOP': 'intermediate',
            'skill_REST_APIs': 'basic',
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Skill assessment saved', resp.data)

        skills = query_db(
            'SELECT skill_name, skill_level FROM skills WHERE user_id=? AND category=?',
            [user['id'], 'software_developer']
        )
        skill_map = {s['skill_name']: s['skill_level'] for s in skills}
        self.assertEqual(skill_map.get('Python'), 'intermediate')
        self.assertEqual(skill_map.get('Git'), 'advanced')

    def test_skill_levels_reload_after_save(self):
        # After saving, GET the page — it should show the saved levels
        resp = self.client.get('/skills?career=software_developer')
        self.assertEqual(resp.status_code, 200)
        data = resp.data.decode('utf-8', 'replace')
        self.assertIn('intermediate', data)

    def test_skill_post_shows_gap_analysis(self):
        resp = self.client.post('/skills?career=software_developer', data={
            'career': 'software_developer',
            'skill_Python': 'intermediate',
            'skill_JavaScript': 'not_learned',
            'skill_Git': 'advanced',
            'skill_SQL': 'not_learned',
            'skill_Data_Structures': 'not_learned',
            'skill_Algorithms': 'not_learned',
            'skill_OOP': 'not_learned',
            'skill_REST_APIs': 'not_learned',
        }, follow_redirects=True)
        data = resp.data.decode('utf-8', 'replace')
        self.assertIn('Skill Readiness', data)


# ── Learning Roadmap ─────────────────────────────────────────────────────────

class TestRoadmap(_BaseTest):

    _username = 'roadmaptest_fixed'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.username = cls._username

    def test_roadmap_page_loads_without_career(self):
        resp = self.client.get('/roadmap')
        self.assertEqual(resp.status_code, 200)

    def test_roadmap_page_loads_with_career(self):
        resp = self.client.get('/roadmap?career=software_developer')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Python Fundamentals', resp.data)

    def test_roadmap_creates_db_record(self):
        user = query_db('SELECT id FROM users WHERE username=?', [self.username], one=True)
        self.client.get('/roadmap?career=data_analyst')
        rm = query_db(
            'SELECT id FROM learning_roadmaps WHERE user_id=? AND career_key=?',
            [user['id'], 'data_analyst'], one=True
        )
        self.assertIsNotNone(rm)

    def test_roadmap_progress_saved(self):
        user = query_db('SELECT id FROM users WHERE username=?', [self.username], one=True)
        resp = self.client.post('/roadmap?career=software_developer', data={
            'career': 'software_developer',
            'completed_steps': ['1', '3', '5'],
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'progress saved', resp.data)

        rm = query_db(
            'SELECT id FROM learning_roadmaps WHERE user_id=? AND career_key=?',
            [user['id'], 'software_developer'], one=True
        )
        self.assertIsNotNone(rm)
        completed = query_db(
            'SELECT step_index FROM roadmap_progress WHERE roadmap_id=? AND completed=1 ORDER BY step_index',
            [rm['id']]
        )
        completed_indices = [r['step_index'] for r in completed]
        self.assertIn(1, completed_indices)
        self.assertIn(3, completed_indices)
        self.assertIn(5, completed_indices)
        self.assertNotIn(2, completed_indices)

    def test_roadmap_progress_reloads_correctly(self):
        # Save progress first, then verify it reloads
        self.client.post('/roadmap?career=software_developer', data={
            'career': 'software_developer',
            'completed_steps': ['2', '4'],
        }, follow_redirects=True)
        resp = self.client.get('/roadmap?career=software_developer')
        self.assertEqual(resp.status_code, 200)
        data = resp.data.decode('utf-8', 'replace')
        self.assertIn('is-done', data)

    def test_roadmap_completion_percentage_shown(self):
        resp = self.client.get('/roadmap?career=software_developer')
        data = resp.data.decode('utf-8', 'replace')
        self.assertIn('%', data)

    def test_roadmap_unknown_career_shows_empty(self):
        # An unknown career key returns selected_career=None (get_career returns None),
        # so the template shows the "Choose Your Learning Path" empty state.
        resp = self.client.get('/roadmap?career=nonexistent_career_xyz')
        self.assertEqual(resp.status_code, 200)
        data = resp.data.decode('utf-8', 'replace')
        # get_career returns None for unknown keys → template shows default empty state
        self.assertIn('Learning Roadmap', data)
        self.assertNotIn('Python Fundamentals', data)

    def test_roadmap_uncheck_all_saves_zero_progress(self):
        user = query_db('SELECT id FROM users WHERE username=?', [self.username], one=True)
        # Submit with no completed_steps
        self.client.post('/roadmap?career=software_developer', data={
            'career': 'software_developer',
        }, follow_redirects=True)
        rm = query_db(
            'SELECT id FROM learning_roadmaps WHERE user_id=? AND career_key=?',
            [user['id'], 'software_developer'], one=True
        )
        completed = query_db(
            'SELECT count(*) as c FROM roadmap_progress WHERE roadmap_id=? AND completed=1',
            [rm['id']], one=True
        )
        self.assertEqual(completed['c'], 0)


# ── Project Ideas ────────────────────────────────────────────────────────────

class TestProjects(_BaseTest):
    _username = 'projtest_fixed'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.username = cls._username

    def test_projects_page_loads(self):
        resp = self.client.get('/projects')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Project Ideas', resp.data)

    def test_projects_filter_by_career(self):
        resp = self.client.get('/projects?career=software_developer')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.status_code, 200)

    def test_projects_filter_by_difficulty(self):
        resp = self.client.get('/projects?difficulty=beginner')
        self.assertEqual(resp.status_code, 200)

    def test_save_project(self):
        user = query_db('SELECT id FROM users WHERE username=?', [self.username], one=True)
        resp = self.client.post('/projects', data={
            'action': 'save', 'project_key': 'expense_tracker', 'status': 'planned',
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Project saved', resp.data)

        saved = query_db(
            'SELECT status FROM project_recommendations WHERE user_id=? AND project_key=?',
            [user['id'], 'expense_tracker'], one=True
        )
        self.assertIsNotNone(saved)
        self.assertEqual(saved['status'], 'planned')

    def test_update_project_status(self):
        user = query_db('SELECT id FROM users WHERE username=?', [self.username], one=True)
        self.client.post('/projects', data={
            'action': 'save', 'project_key': 'weather_app', 'status': 'planned',
        })
        self.client.post('/projects', data={
            'action': 'save', 'project_key': 'weather_app', 'status': 'in_progress',
        })
        saved = query_db(
            'SELECT status FROM project_recommendations WHERE user_id=? AND project_key=?',
            [user['id'], 'weather_app'], one=True
        )
        self.assertEqual(saved['status'], 'in_progress')

    def test_remove_project(self):
        user = query_db('SELECT id FROM users WHERE username=?', [self.username], one=True)
        self.client.post('/projects', data={
            'action': 'save', 'project_key': 'portfolio_website', 'status': 'planned',
        })
        resp = self.client.post('/projects', data={
            'action': 'remove', 'project_key': 'portfolio_website',
        }, follow_redirects=True)
        self.assertIn(b'removed', resp.data)
        saved = query_db(
            'SELECT id FROM project_recommendations WHERE user_id=? AND project_key=?',
            [user['id'], 'portfolio_website'], one=True
        )
        self.assertIsNone(saved)

    def test_saved_projects_shown_on_dashboard(self):
        # Save a project first, then verify it shows on the dashboard
        self.client.post('/projects', data={
            'action': 'save', 'project_key': 'student_management_system', 'status': 'planned',
        })
        resp = self.client.get('/dashboard')
        self.assertEqual(resp.status_code, 200)
        data = resp.data.decode('utf-8', 'replace')
        self.assertIn('student management', data.lower())


# ── Resume Assistant ─────────────────────────────────────────────────────────

class TestResume(_BaseTest):
    _username = 'resumetest_fixed'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.username = cls._username

    def test_resume_page_loads(self):
        resp = self.client.get('/resume')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Resume Assistant', resp.data)

    def test_resume_generation_returns_content(self):
        resp = self.client.post('/resume', data={
            'name': 'Jane Doe',
            'email': 'jane@example.com',
            'phone': '+60 12 345 6789',
            'location': 'Kuala Lumpur, Malaysia',
            'summary': 'Motivated Computer Science graduate with skills in Python and web development.',
            'education': 'BSc Computer Science — XYZ University (2021–2025)',
            'technical_skills': 'Python, Flask, SQLite, HTML, CSS, JavaScript',
            'soft_skills': 'Communication, Teamwork, Problem-solving',
            'projects': 'Student Management System — Flask, SQLite, Bootstrap',
            'certifications': 'Google IT Support Certificate — Coursera (2024)',
            'experience': '',
            'achievements': "Dean's List 2023",
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.data.decode('utf-8', 'replace')
        self.assertIn('JANE DOE', data)
        self.assertIn('Python', data)
        self.assertIn('Resume draft generated', data)

    def test_resume_saved_to_db(self):
        user = query_db('SELECT id FROM users WHERE username=?', [self.username], one=True)
        self.client.post('/resume', data={
            'name': 'Jane Doe', 'email': 'jane@example.com', 'phone': '',
            'location': '', 'summary': 'Skilled developer.',
            'education': 'BSc CS', 'technical_skills': 'Python',
            'soft_skills': '', 'projects': '', 'certifications': '',
            'experience': '', 'achievements': '',
        })
        draft = query_db(
            'SELECT content FROM resume_drafts WHERE user_id=? ORDER BY id DESC LIMIT 1',
            [user['id']], one=True
        )
        self.assertIsNotNone(draft)
        self.assertIn('JANE DOE', draft['content'])

    def test_previous_draft_shown_on_get(self):
        # First ensure a draft exists for this user
        self.client.post('/resume', data={
            'name': 'Test User', 'email': 'test@example.com', 'phone': '',
            'location': '', 'summary': 'Developer.',
            'education': 'BSc CS', 'technical_skills': 'Python',
            'soft_skills': '', 'projects': '', 'certifications': '',
            'experience': '', 'achievements': '',
        })
        resp = self.client.get('/resume')
        self.assertEqual(resp.status_code, 200)
        data = resp.data.decode('utf-8', 'replace')
        self.assertIn('Previous Draft', data)

    def test_resume_empty_name_still_generates(self):
        # Without a name, build_resume uses empty string for name — still generates ok
        resp = self.client.post('/resume', data={
            'name': '', 'email': 'test@example.com', 'phone': '',
            'location': '', 'summary': '',
            'education': '', 'technical_skills': '',
            'soft_skills': '', 'projects': '', 'certifications': '',
            'experience': '', 'achievements': '',
        })
        self.assertEqual(resp.status_code, 200)
        # Should render the resume output area with the email at minimum
        self.assertIn(b'test@example.com', resp.data)
        self.assertIn(b'Resume draft generated', resp.data)


# ── Interview Preparation ────────────────────────────────────────────────────

class TestInterview(_BaseTest):
    _username = 'inttest_fixed'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.username = cls._username

    def test_interview_page_loads(self):
        resp = self.client.get('/interview')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Interview Preparation', resp.data)

    def test_interview_loads_questions(self):
        resp = self.client.post('/interview', data={
            'action': 'get_questions',
            'career_role': 'Software Developer',
            'topic': 'python',
            'difficulty': 'beginner',
        })
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Python', resp.data)
        self.assertIn(b'Practice Questions', resp.data)

    def test_interview_loads_all_topics(self):
        topics = ['python', 'sql', 'data_structures', 'web_development',
                  'artificial_intelligence', 'communication_skills']
        for topic in topics:
            resp = self.client.post('/interview', data={
                'action': 'get_questions',
                'career_role': 'Software Developer',
                'topic': topic,
                'difficulty': 'beginner',
            })
            self.assertEqual(resp.status_code, 200,
                             f'Topic {topic} returned {resp.status_code}')

    def test_interview_loads_all_difficulties(self):
        for diff in ('beginner', 'intermediate', 'advanced'):
            resp = self.client.post('/interview', data={
                'action': 'get_questions',
                'career_role': 'Software Developer',
                'topic': 'python',
                'difficulty': diff,
            })
            self.assertEqual(resp.status_code, 200)

    def test_interview_feedback_returns_structured_response(self):
        resp = self.client.post('/interview/feedback', data={
            'question': 'What is Python and why is it popular?',
            'answer': 'Python is a high-level, interpreted programming language known for its clear syntax and versatility.',
            'career_role': 'Software Developer',
            'topic': 'python',
            'difficulty': 'beginner',
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.data.decode('utf-8', 'replace')
        self.assertIn('What You Explained Well', data)
        self.assertIn('Important Points to Add', data)
        self.assertIn('Suggestions for Improvement', data)
        self.assertIn('Sample Answer', data)

    def test_interview_feedback_saves_topic_and_difficulty(self):
        """Bug fix: topic and difficulty must be saved correctly, not empty/hardcoded."""
        user = query_db('SELECT id FROM users WHERE username=?', [self.username], one=True)
        self.client.post('/interview/feedback', data={
            'question': 'Explain list comprehensions.',
            'answer': 'List comprehensions provide a concise way to create lists in Python.',
            'career_role': 'Software Developer',
            'topic': 'python',
            'difficulty': 'intermediate',
        })
        sess = query_db(
            'SELECT topic, difficulty FROM interview_sessions WHERE user_id=? ORDER BY id DESC LIMIT 1',
            [user['id']], one=True
        )
        self.assertIsNotNone(sess)
        self.assertEqual(sess['topic'], 'python')
        self.assertEqual(sess['difficulty'], 'intermediate')

    def test_interview_feedback_empty_answer_redirects(self):
        resp = self.client.post('/interview/feedback', data={
            'question': 'What is Python?',
            'answer': '',
            'career_role': 'Software Developer',
            'topic': 'python',
            'difficulty': 'beginner',
        })
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/interview', resp.headers['Location'])

    def test_interview_feedback_empty_question_redirects(self):
        resp = self.client.post('/interview/feedback', data={
            'question': '',
            'answer': 'Python is great.',
            'career_role': 'Software Developer',
            'topic': 'python',
            'difficulty': 'beginner',
        })
        self.assertEqual(resp.status_code, 302)

    def test_interview_sessions_shown_on_dashboard(self):
        # Create a session first, then check the dashboard
        self.client.post('/interview/feedback', data={
            'question': 'What is Python?',
            'answer': 'A high-level programming language.',
            'career_role': 'Software Developer',
            'topic': 'python',
            'difficulty': 'beginner',
        })
        resp = self.client.get('/dashboard')
        data = resp.data.decode('utf-8', 'replace')
        self.assertIn('Software Developer', data)


# ── Career Explorer ──────────────────────────────────────────────────────────

class TestCareerExplorer(_BaseTest):

    def test_careers_page_loads(self):
        resp = self.client.get('/careers')
        self.assertEqual(resp.status_code, 200)

    def test_careers_filter_by_category(self):
        resp = self.client.get('/careers?category=technology')
        self.assertEqual(resp.status_code, 200)

    def test_careers_search(self):
        resp = self.client.get('/careers?search=python')
        self.assertEqual(resp.status_code, 200)

    def test_career_detail_loads(self):
        resp = self.client.get('/careers/software_developer')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Software Developer', resp.data)

    def test_career_detail_404_for_unknown(self):
        resp = self.client.get('/careers/nonexistent_career_xyz')
        self.assertEqual(resp.status_code, 404)

    def test_all_career_details_load(self):
        from services.career_engine import CAREERS
        for career in CAREERS:
            resp = self.client.get(f'/careers/{career["key"]}')
            self.assertEqual(resp.status_code, 200,
                             f'/careers/{career["key"]} returned {resp.status_code}')


# ── API Endpoints ────────────────────────────────────────────────────────────

class TestApiEndpoints(_BaseTest):

    def test_api_careers_returns_json(self):
        resp = self.client.get('/api/careers')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        data = json.loads(resp.data)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)

    def test_api_careers_has_required_fields(self):
        resp = self.client.get('/api/careers')
        data = json.loads(resp.data)
        for career in data:
            self.assertIn('key', career)
            self.assertIn('title', career)
            self.assertIn('category', career)

    def test_api_roadmap_returns_json(self):
        resp = self.client.get('/api/roadmap/software_developer')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)

    def test_api_roadmap_unknown_career_returns_empty(self):
        resp = self.client.get('/api/roadmap/nonexistent_key_xyz')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        # get_roadmap returns [] (empty list) for unknown career keys
        self.assertEqual(data, [])


# ── Error Handlers ───────────────────────────────────────────────────────────

class TestErrorHandlers(_BaseTest):

    def test_404_page(self):
        resp = self.client.get('/this_route_does_not_exist_xyz')
        self.assertEqual(resp.status_code, 404)
        self.assertIn(b'404', resp.data)

    def test_403_page(self):
        # A regular user trying to access /admin
        username = _unique('forbtest')
        self.client.post('/register', data={
            'username': username, 'email': f'{username}@test.local',
            'password': 'TestPass1!', 'education_level': 'undergraduate',
        })
        resp = self.client.get('/admin')
        self.assertEqual(resp.status_code, 403)
        self.assertIn(b'403', resp.data)
        self._logout()


if __name__ == '__main__':
    unittest.main(verbosity=2)
