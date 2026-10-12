"""
Tests for database operations.
"""

import sys
import os
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestDatabaseInit(unittest.TestCase):

    def setUp(self):
        """Create a temporary database for each test."""
        import app as application
        self.db_fd, self.db_path = tempfile.mkstemp(suffix='.db')
        self.app = application.create_app('development')
        self.app.config['DATABASE_PATH'] = self.db_path
        self.app.config['TESTING'] = True
        self.app.config['SECRET_KEY'] = 'test-secret'
        self.ctx = self.app.app_context()
        self.ctx.push()

        from models.database import init_db
        init_db()

    def tearDown(self):
        self.ctx.pop()
        os.close(self.db_fd)
        try:
            os.unlink(self.db_path)
        except Exception:
            pass

    def test_tables_created(self):
        """All required tables should exist after init."""
        from models.database import query_db
        tables = query_db(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        table_names = [t['name'] for t in tables]
        required = [
            'users', 'student_profiles', 'career_recommendations',
            'skills', 'learning_roadmaps', 'roadmap_progress',
            'project_recommendations', 'interview_sessions', 'resume_drafts',
        ]
        for table in required:
            self.assertIn(table, table_names, f"Table '{table}' not found")

    def test_user_registration(self):
        """Should be able to insert and retrieve a user."""
        from models.database import execute_db, query_db
        from werkzeug.security import generate_password_hash, check_password_hash

        uid = execute_db(
            'INSERT INTO users (username, email, password_hash, education_level) VALUES (?,?,?,?)',
            ['testuser', 'test@example.com', generate_password_hash('Test1234!'), 'undergraduate']
        )
        self.assertIsNotNone(uid)
        self.assertGreater(uid, 0)

        user = query_db('SELECT * FROM users WHERE id = ?', [uid], one=True)
        self.assertIsNotNone(user)
        self.assertEqual(user['username'], 'testuser')
        self.assertEqual(user['email'], 'test@example.com')
        self.assertTrue(check_password_hash(user['password_hash'], 'Test1234!'))
        self.assertFalse(check_password_hash(user['password_hash'], 'WrongPassword'))

    def test_duplicate_username_rejected(self):
        """Duplicate usernames should raise an integrity error."""
        from models.database import execute_db
        from werkzeug.security import generate_password_hash
        import sqlite3

        execute_db(
            'INSERT INTO users (username, email, password_hash) VALUES (?,?,?)',
            ['dupeuser', 'dupe1@example.com', generate_password_hash('Test1234!')]
        )
        with self.assertRaises(sqlite3.IntegrityError):
            execute_db(
                'INSERT INTO users (username, email, password_hash) VALUES (?,?,?)',
                ['dupeuser', 'dupe2@example.com', generate_password_hash('Test1234!')]
            )

    def test_student_profile_crud(self):
        """Student profile should link to user correctly."""
        from models.database import execute_db, query_db
        from werkzeug.security import generate_password_hash

        uid = execute_db(
            'INSERT INTO users (username, email, password_hash) VALUES (?,?,?)',
            ['profiletest', 'profile@example.com', generate_password_hash('Test1234!')]
        )
        execute_db('INSERT INTO student_profiles (user_id, interests, technical_skills) VALUES (?,?,?)',
                   [uid, 'coding, AI', 'Python, SQL'])

        profile = query_db('SELECT * FROM student_profiles WHERE user_id = ?', [uid], one=True)
        self.assertIsNotNone(profile)
        self.assertEqual(profile['interests'], 'coding, AI')

    def test_admin_user_seeded(self):
        """Admin user should be seeded on init."""
        from models.database import query_db, seed_admin
        seed_admin()
        admin = query_db("SELECT * FROM users WHERE role = 'admin' LIMIT 1", one=True)
        self.assertIsNotNone(admin)
        self.assertEqual(admin['role'], 'admin')
        self.assertEqual(admin['username'], 'admin')

    def test_parameterised_queries(self):
        """Parameterised queries should prevent SQL injection."""
        from models.database import query_db

        # Attempt SQL injection in query parameter - should return empty, not all users
        result = query_db(
            "SELECT * FROM users WHERE username = ?",
            ["' OR '1'='1"]
        )
        self.assertEqual(len(result), 0)


class TestFlaskRoutes(unittest.TestCase):

    def setUp(self):
        import app as application
        self.db_fd, self.db_path = tempfile.mkstemp(suffix='.db')
        flask_app = application.create_app('development')
        flask_app.config['DATABASE_PATH'] = self.db_path
        flask_app.config['TESTING'] = True
        flask_app.config['SECRET_KEY'] = 'test-secret'
        flask_app.config['WTF_CSRF_ENABLED'] = False
        self.client = flask_app.test_client()
        self.ctx = flask_app.app_context()
        self.ctx.push()
        from models.database import init_db
        init_db()

    def tearDown(self):
        self.ctx.pop()
        os.close(self.db_fd)
        try:
            os.unlink(self.db_path)
        except Exception:
            pass

    def test_home_page_loads(self):
        """Home page should return 200."""
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'CareerPath AI', resp.data)

    def test_careers_page_loads(self):
        """Careers page should load without authentication."""
        resp = self.client.get('/careers')
        self.assertEqual(resp.status_code, 200)

    def test_about_page_loads(self):
        """About page should load without authentication."""
        resp = self.client.get('/about')
        self.assertEqual(resp.status_code, 200)

    def test_login_page_loads(self):
        resp = self.client.get('/login')
        self.assertEqual(resp.status_code, 200)

    def test_register_page_loads(self):
        resp = self.client.get('/register')
        self.assertEqual(resp.status_code, 200)

    def test_dashboard_requires_login(self):
        """Dashboard should redirect unauthenticated users to login."""
        resp = self.client.get('/dashboard', follow_redirects=False)
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/login', resp.headers['Location'])

    def test_user_registration_and_login(self):
        """User can register and then log in."""
        # Register
        resp = self.client.post('/register', data={
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'Test1234!',
            'education_level': 'undergraduate',
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

        # Logout
        self.client.get('/logout')

        # Login
        resp = self.client.post('/login', data={
            'identifier': 'testuser',
            'password': 'Test1234!',
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Welcome', resp.data)

    def test_invalid_login_rejected(self):
        """Invalid credentials should show error."""
        resp = self.client.post('/login', data={
            'identifier': 'nobody',
            'password': 'wrongpassword',
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Invalid', resp.data)

    def test_404_page(self):
        """Non-existent route should return 404."""
        resp = self.client.get('/this-page-does-not-exist')
        self.assertEqual(resp.status_code, 404)


if __name__ == '__main__':
    unittest.main()
