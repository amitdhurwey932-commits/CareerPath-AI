"""
CareerPath AI — Main Flask Application
"""

import os
import json
import random
from functools import wraps
from datetime import datetime

from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, jsonify, abort, g
)
from werkzeug.security import generate_password_hash, check_password_hash

from config import config
from models.database import init_app, query_db, execute_db
from services.career_engine import (
    get_all_careers, get_career, get_careers_by_category,
    recommend_careers, get_skill_gap, validate_profile,
)
from services.roadmap_service import get_roadmap, get_all_roadmap_keys
from services.resume_service import build_resume, get_resume_tips
from services.interview_service import get_questions, get_available_topics, get_available_careers
from services import ai_service


# ──────────────────────────────────────────────────────────
# Application factory
# ──────────────────────────────────────────────────────────

def create_app(env: str = None) -> Flask:
    app = Flask(__name__)
    env = env or os.environ.get('FLASK_ENV', 'development')
    app.config.from_object(config.get(env, config['default']))

    # Load .env if python-dotenv is available
    try:
        from dotenv import load_dotenv
        load_dotenv()
        # Re-apply env-dependent config after loading .env
        app.config['AI_API_KEY'] = os.environ.get('AI_API_KEY', '')
        app.config['AI_DEMO_MODE'] = not bool(app.config['AI_API_KEY'])
        if os.environ.get('SECRET_KEY'):
            app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    except ImportError:
        pass

    init_app(app)
    register_routes(app)
    return app


# ──────────────────────────────────────────────────────────
# Auth helpers
# ──────────────────────────────────────────────────────────

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in.', 'warning')
            return redirect(url_for('login'))
        user = query_db('SELECT role FROM users WHERE id = ?', [session['user_id']], one=True)
        if not user or user['role'] != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated


def current_user():
    if 'user_id' not in session:
        return None
    return query_db('SELECT * FROM users WHERE id = ?', [session['user_id']], one=True)


# ──────────────────────────────────────────────────────────
# Route registration
# ──────────────────────────────────────────────────────────

def register_routes(app: Flask):

    # ── Context processor ──────────────────────────────────
    @app.context_processor
    def inject_user():
        user = current_user()
        demo_mode = app.config.get('AI_DEMO_MODE', True)
        return dict(current_user=user, ai_demo_mode=demo_mode)

    # ── Error handlers ─────────────────────────────────────
    @app.errorhandler(403)
    def forbidden(e):
        return render_template('error.html', code=403, message='Access Forbidden'), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template('error.html', code=404, message='Page Not Found'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('error.html', code=500, message='Internal Server Error'), 500

    # ── Public routes ──────────────────────────────────────

    @app.route('/')
    def index():
        careers = get_all_careers()
        return render_template('index.html', careers=careers)

    @app.route('/about')
    def about():
        return render_template('about.html')

    # ── Auth ───────────────────────────────────────────────

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if 'user_id' in session:
            return redirect(url_for('dashboard'))

        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')
            education_level = request.form.get('education_level', '').strip()

            errors = []
            if not username or len(username) < 3:
                errors.append('Username must be at least 3 characters.')
            if not email or '@' not in email:
                errors.append('Please enter a valid email address.')
            if not password or len(password) < 8:
                errors.append('Password must be at least 8 characters.')
            if not education_level:
                errors.append('Please select your education level.')

            if not errors:
                existing = query_db(
                    'SELECT id FROM users WHERE username = ? OR email = ?',
                    [username, email], one=True
                )
                if existing:
                    errors.append('Username or email is already registered.')

            if errors:
                for err in errors:
                    flash(err, 'danger')
                return render_template('register.html',
                                       form_data={'username': username, 'email': email, 'education_level': education_level})

            uid = execute_db(
                'INSERT INTO users (username, email, password_hash, education_level) VALUES (?, ?, ?, ?)',
                [username, email, generate_password_hash(password), education_level]
            )
            # Create empty profile
            execute_db('INSERT INTO student_profiles (user_id) VALUES (?)', [uid])
            session.permanent = True
            session['user_id'] = uid
            session['username'] = username
            flash(f'Welcome, {username}! Your account has been created.', 'success')
            return redirect(url_for('dashboard'))

        return render_template('register.html', form_data={})

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if 'user_id' in session:
            return redirect(url_for('dashboard'))

        if request.method == 'POST':
            identifier = request.form.get('identifier', '').strip()
            password = request.form.get('password', '')

            user = query_db(
                'SELECT * FROM users WHERE username = ? OR email = ?',
                [identifier, identifier.lower()], one=True
            )
            if user and check_password_hash(user['password_hash'], password):
                session.permanent = True
                session['user_id'] = user['id']
                session['username'] = user['username']
                flash(f'Welcome back, {user["username"]}!', 'success')
                next_url = request.args.get('next')
                return redirect(next_url if next_url and next_url.startswith('/') else url_for('dashboard'))
            else:
                flash('Invalid username/email or password.', 'danger')

        return render_template('login.html')

    @app.route('/logout')
    def logout():
        session.clear()
        flash('You have been logged out.', 'info')
        return redirect(url_for('index'))

    # ── Dashboard ──────────────────────────────────────────

    @app.route('/dashboard')
    @login_required
    def dashboard():
        uid = session['user_id']
        user = query_db('SELECT * FROM users WHERE id = ?', [uid], one=True)
        profile = query_db('SELECT * FROM student_profiles WHERE user_id = ?', [uid], one=True)
        recommendations = query_db(
            'SELECT * FROM career_recommendations WHERE user_id = ? ORDER BY match_score DESC LIMIT 5',
            [uid]
        )
        skills = query_db('SELECT * FROM skills WHERE user_id = ?', [uid])
        roadmaps = query_db('SELECT * FROM learning_roadmaps WHERE user_id = ?', [uid])
        saved_projects = query_db(
            'SELECT * FROM project_recommendations WHERE user_id = ? ORDER BY created_at DESC',
            [uid]
        )
        interview_sessions = query_db(
            'SELECT * FROM interview_sessions WHERE user_id = ? ORDER BY created_at DESC LIMIT 5',
            [uid]
        )

        # Compute roadmap progress for each saved roadmap
        roadmap_progress = {}
        for rm in roadmaps:
            steps = query_db(
                'SELECT * FROM roadmap_progress WHERE roadmap_id = ?', [rm['id']]
            )
            completed = sum(1 for s in steps if s['completed'])
            total = len(steps)
            roadmap_progress[rm['career_key']] = {
                'completed': completed,
                'total': total,
                'pct': round(completed / total * 100) if total else 0,
            }

        return render_template(
            'dashboard.html',
            user=user, profile=profile,
            recommendations=recommendations,
            skills=skills, roadmaps=roadmaps,
            roadmap_progress=roadmap_progress,
            saved_projects=saved_projects,
            interview_sessions=interview_sessions,
        )

    # ── Profile ─────────────────────────────────────────────

    @app.route('/profile', methods=['GET', 'POST'])
    @login_required
    def profile():
        uid = session['user_id']
        user = query_db('SELECT * FROM users WHERE id = ?', [uid], one=True)
        prof = query_db('SELECT * FROM student_profiles WHERE user_id = ?', [uid], one=True)

        if request.method == 'POST':
            fields = {
                'degree_course': request.form.get('degree_course', '').strip(),
                'interests': request.form.get('interests', '').strip(),
                'technical_skills': request.form.get('technical_skills', '').strip(),
                'soft_skills': request.form.get('soft_skills', '').strip(),
                'experience_level': request.form.get('experience_level', 'beginner').strip(),
                'preferred_field': request.form.get('preferred_field', '').strip(),
                'career_goals': request.form.get('career_goals', '').strip(),
            }
            execute_db(
                '''UPDATE student_profiles SET
                   degree_course=?, interests=?, technical_skills=?,
                   soft_skills=?, experience_level=?, preferred_field=?,
                   career_goals=?, updated_at=CURRENT_TIMESTAMP
                   WHERE user_id=?''',
                [*fields.values(), uid]
            )
            flash('Profile updated successfully.', 'success')
            return redirect(url_for('profile'))

        return render_template('profile.html', user=user, profile=prof)

    # ── Career recommendations ─────────────────────────────

    @app.route('/recommend', methods=['GET', 'POST'])
    @login_required
    def recommend():
        uid = session['user_id']
        user = query_db('SELECT * FROM users WHERE id = ?', [uid], one=True)
        profile = query_db('SELECT * FROM student_profiles WHERE user_id = ?', [uid], one=True)
        results = []

        validation_errors = []

        if request.method == 'POST':
            raw_profile = {
                'education_level': request.form.get('education_level', ''),
                'degree_course':   request.form.get('degree_course', ''),
                'interests':       request.form.get('interests', ''),
                'technical_skills':request.form.get('technical_skills', ''),
                'soft_skills':     request.form.get('soft_skills', ''),
                'experience_level':request.form.get('experience_level', 'beginner'),
                'preferred_field': request.form.get('preferred_field', ''),
                'career_goals':    request.form.get('career_goals', ''),
            }

            # Validate and clean before passing to the engine
            form_profile, validation_errors = validate_profile(raw_profile)

            results = recommend_careers(form_profile)

            # Optionally enhance with AI
            for r in results:
                r['ai_explanation'] = ai_service.enhance_career_explanation(
                    r['career']['title'], r['match_reasons'], form_profile
                )

            # Save top recommendations to DB (skip fallback-only results)
            execute_db('DELETE FROM career_recommendations WHERE user_id = ?', [uid])
            for r in results:
                reasons_json = json.dumps(r['match_reasons'])
                execute_db(
                    'INSERT INTO career_recommendations '
                    '(user_id, career_key, match_score, match_reason) VALUES (?,?,?,?)',
                    [uid, r['career']['key'], r['match_score'], reasons_json]
                )

            # Update profile from cleaned form data
            execute_db(
                '''UPDATE student_profiles SET
                   degree_course=?, interests=?, technical_skills=?,
                   soft_skills=?, experience_level=?, preferred_field=?,
                   career_goals=?, updated_at=CURRENT_TIMESTAMP
                   WHERE user_id=?''',
                [
                    form_profile['degree_course'], form_profile['interests'],
                    form_profile['technical_skills'], form_profile['soft_skills'],
                    form_profile['experience_level'], form_profile['preferred_field'],
                    form_profile['career_goals'], uid,
                ]
            )

        return render_template(
            'recommend.html',
            user=user, profile=profile,
            results=results,
            validation_errors=validation_errors,
            careers=get_all_careers(),
        )

    # ── Career explorer ────────────────────────────────────

    @app.route('/careers')
    def careers():
        category = request.args.get('category', '')
        search = request.args.get('search', '').lower()

        all_careers = get_all_careers()
        if category:
            all_careers = [c for c in all_careers if c['category'] == category]
        if search:
            all_careers = [
                c for c in all_careers
                if search in c['title'].lower() or search in c['description'].lower()
                or any(search in kw for kw in c.get('keywords', []))
            ]

        categories = list({c['category'] for c in get_all_careers()})
        return render_template('careers.html', careers=all_careers, categories=categories,
                               selected_category=category, search=search)

    @app.route('/careers/<career_key>')
    def career_detail(career_key):
        career = get_career(career_key)
        if not career:
            abort(404)

        # Load projects for this career
        projects_path = os.path.join(app.root_path, 'data', 'projects.json')
        with open(projects_path, 'r') as f:
            all_projects = json.load(f)
        related_projects = [p for p in all_projects if career_key in p.get('careers', [])]

        roadmap = get_roadmap(career_key)

        return render_template('career_detail.html', career=career,
                               related_projects=related_projects, roadmap=roadmap)

    # ── Skill assessment ───────────────────────────────────

    @app.route('/skills', methods=['GET', 'POST'])
    @login_required
    def skill_assessment():
        uid = session['user_id']
        all_careers = get_all_careers()
        selected_career_key = request.args.get('career', '') or request.form.get('career', '')
        selected_career = get_career(selected_career_key) if selected_career_key else None

        skill_data = None
        user_skill_levels = {}

        if request.method == 'POST' and selected_career_key:
            # Save skill levels from form
            for skill in selected_career.get('required_skills', []):
                level = request.form.get(f'skill_{skill.replace(" ", "_")}', 'not_learned')
                execute_db(
                    '''INSERT INTO skills (user_id, skill_name, skill_level, category)
                       VALUES (?, ?, ?, ?)
                       ON CONFLICT(user_id, skill_name) DO UPDATE SET skill_level=?''',
                    [uid, skill, level, selected_career_key, level]
                )
                user_skill_levels[skill] = level

            skill_data = get_skill_gap(selected_career_key, [
                s for s, lvl in user_skill_levels.items()
                if lvl not in ('not_learned', 'basic')
            ])
            flash('Skill assessment saved.', 'success')
        elif selected_career:
            # Load existing skill levels
            saved = query_db(
                'SELECT skill_name, skill_level FROM skills WHERE user_id = ? AND category = ?',
                [uid, selected_career_key]
            )
            user_skill_levels = {row['skill_name']: row['skill_level'] for row in saved}
            skill_data = get_skill_gap(selected_career_key, [
                s for s, lvl in user_skill_levels.items()
                if lvl not in ('not_learned', 'basic')
            ])

        return render_template(
            'skill_assessment.html',
            careers=all_careers,
            selected_career=selected_career,
            skill_data=skill_data,
            user_skill_levels=user_skill_levels,
        )

    # ── Learning roadmap ───────────────────────────────────

    @app.route('/roadmap', methods=['GET', 'POST'])
    @login_required
    def roadmap():
        uid = session['user_id']
        all_careers = get_all_careers()
        selected_career_key = request.args.get('career', '') or request.form.get('career', '')
        selected_career = get_career(selected_career_key) if selected_career_key else None

        roadmap_data = None
        progress_data = {}
        pct = 0

        if selected_career_key:
            steps = get_roadmap(selected_career_key)
            if steps:
                # Ensure roadmap record exists
                existing_rm = query_db(
                    'SELECT id FROM learning_roadmaps WHERE user_id = ? AND career_key = ?',
                    [uid, selected_career_key], one=True
                )
                if not existing_rm:
                    rm_id = execute_db(
                        'INSERT INTO learning_roadmaps (user_id, career_key) VALUES (?, ?)',
                        [uid, selected_career_key]
                    )
                    # Insert progress rows
                    for step in steps:
                        execute_db(
                            'INSERT OR IGNORE INTO roadmap_progress (roadmap_id, step_index, topic) VALUES (?,?,?)',
                            [rm_id, step['step'], step['topic']]
                        )
                    existing_rm = query_db(
                        'SELECT id FROM learning_roadmaps WHERE user_id = ? AND career_key = ?',
                        [uid, selected_career_key], one=True
                    )
                rm_id = existing_rm['id']

                if request.method == 'POST':
                    completed_steps = request.form.getlist('completed_steps')
                    # Reset all, then mark completed
                    execute_db('UPDATE roadmap_progress SET completed=0, completed_at=NULL WHERE roadmap_id=?', [rm_id])
                    for step_idx in completed_steps:
                        execute_db(
                            'UPDATE roadmap_progress SET completed=1, completed_at=CURRENT_TIMESTAMP WHERE roadmap_id=? AND step_index=?',
                            [rm_id, int(step_idx)]
                        )
                    flash('Roadmap progress saved.', 'success')

                # Load progress
                progress_rows = query_db(
                    'SELECT step_index, completed FROM roadmap_progress WHERE roadmap_id = ?', [rm_id]
                )
                progress_data = {row['step_index']: bool(row['completed']) for row in progress_rows}
                completed_count = sum(1 for v in progress_data.values() if v)
                pct = round(completed_count / len(steps) * 100) if steps else 0
                roadmap_data = steps

        return render_template(
            'roadmap.html',
            careers=all_careers,
            selected_career=selected_career,
            roadmap_data=roadmap_data,
            progress_data=progress_data,
            completion_pct=pct,
        )

    # ── Project ideas ──────────────────────────────────────

    @app.route('/projects', methods=['GET', 'POST'])
    @login_required
    def projects():
        uid = session['user_id']
        projects_path = os.path.join(app.root_path, 'data', 'projects.json')
        with open(projects_path, 'r') as f:
            all_projects = json.load(f)

        career_filter = request.args.get('career', '')
        difficulty_filter = request.args.get('difficulty', '')

        filtered = all_projects
        if career_filter:
            filtered = [p for p in filtered if career_filter in p.get('careers', [])]
        if difficulty_filter:
            filtered = [p for p in filtered if p.get('difficulty') == difficulty_filter]

        # Load saved project statuses
        saved = query_db('SELECT project_key, status FROM project_recommendations WHERE user_id = ?', [uid])
        saved_map = {row['project_key']: row['status'] for row in saved}

        if request.method == 'POST':
            action = request.form.get('action')
            project_key = request.form.get('project_key')
            status = request.form.get('status', 'planned')
            if action == 'save':
                execute_db(
                    '''INSERT INTO project_recommendations (user_id, project_key, status)
                       VALUES (?,?,?)
                       ON CONFLICT(user_id, project_key) DO UPDATE SET status=?''',
                    [uid, project_key, status, status]
                )
                saved_map[project_key] = status
                flash('Project saved to your dashboard.', 'success')
            elif action == 'remove':
                execute_db(
                    'DELETE FROM project_recommendations WHERE user_id=? AND project_key=?',
                    [uid, project_key]
                )
                saved_map.pop(project_key, None)
                flash('Project removed from your dashboard.', 'info')
            return redirect(url_for('projects', career=career_filter, difficulty=difficulty_filter))

        return render_template(
            'projects.html',
            projects=filtered,
            all_projects=all_projects,
            careers=get_all_careers(),
            saved_map=saved_map,
            career_filter=career_filter,
            difficulty_filter=difficulty_filter,
        )

    # ── Resume assistant ───────────────────────────────────

    @app.route('/resume', methods=['GET', 'POST'])
    @login_required
    def resume():
        uid = session['user_id']
        user = query_db('SELECT * FROM users WHERE id = ?', [uid], one=True)
        profile = query_db('SELECT * FROM student_profiles WHERE user_id = ?', [uid], one=True)
        tips = get_resume_tips()
        resume_content = None
        saved_draft = query_db(
            'SELECT * FROM resume_drafts WHERE user_id = ? ORDER BY created_at DESC LIMIT 1', [uid], one=True
        )

        if request.method == 'POST':
            data = {
                'name': request.form.get('name', '').strip(),
                'email': request.form.get('email', user['email'] if user else '').strip(),
                'phone': request.form.get('phone', '').strip(),
                'location': request.form.get('location', '').strip(),
                'summary': request.form.get('summary', '').strip(),
                'education': request.form.get('education', '').strip(),
                'technical_skills': request.form.get('technical_skills', '').strip(),
                'soft_skills': request.form.get('soft_skills', '').strip(),
                'projects': request.form.get('projects', '').strip(),
                'certifications': request.form.get('certifications', '').strip(),
                'experience': request.form.get('experience', '').strip(),
                'achievements': request.form.get('achievements', '').strip(),
            }
            resume_content = build_resume(data)

            # Optionally improve with AI
            if data['summary']:
                improved = ai_service.improve_resume_section('Professional Summary', data['summary'])
                if improved and improved != data['summary']:
                    resume_content = resume_content.replace(data['summary'], improved)

            # Save draft
            execute_db(
                'INSERT INTO resume_drafts (user_id, content) VALUES (?,?)',
                [uid, resume_content]
            )
            flash('Resume draft generated and saved.', 'success')

        return render_template(
            'resume.html',
            user=user, profile=profile,
            resume_content=resume_content,
            saved_draft=saved_draft,
            tips=tips,
        )

    # ── Interview preparation ──────────────────────────────

    @app.route('/interview', methods=['GET', 'POST'])
    @login_required
    def interview():
        uid = session['user_id']
        topics = get_available_topics()
        career_roles = get_available_careers()
        questions = []
        selected_topic = ''
        selected_role = ''
        selected_difficulty = 'beginner'
        session_id = None

        if request.method == 'POST' and request.form.get('action') == 'get_questions':
            selected_topic = request.form.get('topic', '')
            selected_role = request.form.get('career_role', '')
            selected_difficulty = request.form.get('difficulty', 'beginner')
            questions = get_questions(selected_topic, selected_difficulty, selected_role)

        return render_template(
            'interview.html',
            topics=topics,
            career_roles=career_roles,
            questions=questions,
            selected_topic=selected_topic,
            selected_role=selected_role,
            selected_difficulty=selected_difficulty,
        )

    @app.route('/interview/feedback', methods=['POST'])
    @login_required
    def interview_feedback():
        uid = session['user_id']
        question   = request.form.get('question', '').strip()
        answer     = request.form.get('answer', '').strip()
        role       = request.form.get('career_role', '').strip()
        topic      = request.form.get('topic', '').strip()
        difficulty = request.form.get('difficulty', 'beginner').strip()

        if not question or not answer:
            flash('Please provide both a question and an answer.', 'warning')
            return redirect(url_for('interview'))

        feedback = ai_service.generate_interview_feedback(question, answer, role)

        # Save session — persist topic and difficulty from the form
        execute_db(
            '''INSERT INTO interview_sessions
               (user_id, career_role, topic, difficulty, question, user_answer, feedback)
               VALUES (?,?,?,?,?,?,?)''',
            [uid, role, topic, difficulty, question, answer, json.dumps(feedback)]
        )

        return render_template(
            'interview_feedback.html',
            question=question, answer=answer,
            feedback=feedback, role=role,
            topic=topic, difficulty=difficulty,
        )

    # ── Admin routes ───────────────────────────────────────

    @app.route('/admin')
    @admin_required
    def admin_dashboard():
        users = query_db('SELECT id, username, email, education_level, role, created_at FROM users ORDER BY created_at DESC')
        total_recommendations = query_db('SELECT COUNT(*) as c FROM career_recommendations', one=True)['c']
        total_sessions = query_db('SELECT COUNT(*) as c FROM interview_sessions', one=True)['c']
        total_drafts = query_db('SELECT COUNT(*) as c FROM resume_drafts', one=True)['c']
        return render_template(
            'admin/dashboard.html',
            users=users,
            stats={
                'users': len(users),
                'recommendations': total_recommendations,
                'interview_sessions': total_sessions,
                'resume_drafts': total_drafts,
            }
        )

    @app.route('/privacy')
    def privacy():
        return render_template('privacy.html')

    # ── Health check ───────────────────────────────────────

    @app.route('/health')
    def health():
        """Lightweight liveness probe for load balancers and uptime monitors."""
        try:
            query_db('SELECT 1', one=True)
            db_ok = True
        except Exception:
            db_ok = False
        payload = {
            'status': 'ok' if db_ok else 'degraded',
            'database': 'ok' if db_ok else 'error',
        }
        return jsonify(payload), 200 if db_ok else 503

    # ── API endpoints (JSON) ───────────────────────────────

    @app.route('/api/careers')
    def api_careers():
        return jsonify(get_all_careers())

    @app.route('/api/roadmap/<career_key>')
    def api_roadmap(career_key):
        return jsonify(get_roadmap(career_key))


# ──────────────────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────────────────

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
