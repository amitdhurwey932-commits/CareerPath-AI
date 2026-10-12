# CareerPath AI 🎓

**AI-Powered Career Guidance Assistant**

CareerPath AI is a full-stack Flask web application that helps college students, fresh graduates, and job seekers explore suitable career paths based on their education, interests, skills, and career goals.

**Project Category:** Artificial Intelligence, Career Guidance, and Skill Development  
**SDG Alignment:** SDG 8 — Decent Work and Economic Growth

---

## Features

| Feature | Description |
|---|---|
| 🌟 AI Career Recommendations | Personalised career matching using rule-based engine + optional AI API |
| 📊 Skill Gap Analysis | Compare current skills against career requirements with visual indicators |
| 🗺️ Learning Roadmaps | Step-by-step learning paths for 8 career areas with progress tracking |
| 💡 Project Ideas | Curated projects by career and difficulty to build your portfolio |
| 📄 Resume Assistant | Generate structured resume drafts from your own information |
| 🎤 Interview Preparation | Practise questions with constructive AI-powered feedback |
| 🏠 Student Dashboard | Track all your progress in one place |
| 🔐 User Authentication | Secure registration, login, and session management |
| 👩‍💼 Admin Panel | View user statistics and manage the platform |

---

## Quick Start (Local Development)

### 1. Prerequisites

- Python 3.9 or later
- pip (Python package manager)

### 2. Clone or Download the Project

```bash
git clone https://github.com/yourusername/careerpath-ai.git
cd careerpath-ai
```

### 3. Create a Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

```bash
# Copy the example file
cp .env.example .env   # macOS/Linux
copy .env.example .env  # Windows
```

Edit `.env` with your settings. At minimum, set a strong `SECRET_KEY` and change `ADMIN_PASSWORD`:

```ini
SECRET_KEY=<output of: python -c "import secrets; print(secrets.token_hex(32))">
ADMIN_PASSWORD=YourStrongAdminPassword1!
```

**Optional — to enable AI features:**

```ini
AI_API_KEY=your-openai-api-key
AI_API_URL=https://api.openai.com/v1/chat/completions
AI_MODEL=gpt-3.5-turbo
```

> **Demo Mode:** Leave `AI_API_KEY` empty to run without an API key.  
> All rule-based features (recommendations, skill gap, roadmaps, projects, resume builder) work fully in demo mode.

### 6. Run Locally

```bash
# Development server (do NOT use in production)
python app.py
```

Open your browser at **http://localhost:5000**

---

## Default Admin Credentials

> ⚠️ **Change `ADMIN_PASSWORD` in `.env` before first deployment. The default only applies when no admin account exists yet.**

| Field | Value |
|---|---|
| Username | `admin` (override with `ADMIN_USERNAME`) |
| Password | set via `ADMIN_PASSWORD` in `.env` |
| Admin URL | http://localhost:5000/admin |

---

## Project Structure

```
careerpath-ai/
│
├── app.py                    # Flask application factory and routes
├── wsgi.py                   # Production WSGI entry point (ProxyFix applied here)
├── config.py                 # Development / Production / Testing config classes
├── gunicorn.conf.py          # Gunicorn tuning (workers, timeouts, logging)
├── nginx.conf.example        # Nginx reverse proxy + Let's Encrypt template
├── render.yaml               # Render Blueprint (auto-configures the service)
├── requirements.txt          # Python dependencies
├── Procfile                  # Heroku / Railway process declaration
├── README.md                 # This file
├── .env.example              # Environment variable template (commit this)
├── .env                      # Your local secrets (DO NOT commit)
│
├── models/
│   └── database.py           # SQLite schema, migrations, helpers
│
├── services/
│   ├── career_engine.py      # Career recommendation logic
│   ├── ai_service.py         # AI API integration (with rule-based fallback)
│   ├── roadmap_service.py    # Learning roadmap data
│   ├── resume_service.py     # Resume builder
│   └── interview_service.py  # Interview questions & feedback
│
├── templates/                # Jinja2 HTML templates
├── static/                   # CSS, JS, images
├── data/                     # careers.json, projects.json
└── tests/                    # Automated test suite
```

---

## Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run a specific file
python -m pytest tests/test_career_engine.py -v
python -m pytest tests/test_database.py -v
python -m pytest tests/test_integration.py -v
```

Tests use a temporary in-memory / temp-file database and never touch `careerpath.db`.

---

## AI API Setup

CareerPath AI supports any **OpenAI-compatible** chat completion endpoint.

### Option 1 — OpenAI (cloud)

1. Create an account at https://platform.openai.com
2. Generate an API key under **API keys**
3. Add to `.env`:

```ini
AI_API_KEY=sk-...
AI_API_URL=https://api.openai.com/v1/chat/completions
AI_MODEL=gpt-3.5-turbo   # or gpt-4
```

### Option 2 — Azure OpenAI

1. Create an Azure OpenAI resource and deploy a model
2. Add to `.env`:

```ini
AI_API_KEY=<your-azure-key>
AI_API_URL=https://<resource>.openai.azure.com/openai/deployments/<deployment>/chat/completions?api-version=2024-02-01
AI_MODEL=gpt-35-turbo
```

### Option 3 — Local model via Ollama (free, offline)

1. Install Ollama: https://ollama.com
2. Pull a model: `ollama pull llama3`
3. Add to `.env`:

```ini
AI_API_URL=http://localhost:11434/v1/chat/completions
AI_MODEL=llama3
AI_API_KEY=ollama
```

### Demo Mode (default — no key required)

When `AI_API_KEY` is empty, all AI routes fall back to rule-based logic:

| Feature | Demo fallback |
|---|---|
| Career recommendations | Keyword and skill-matching algorithm |
| Interview feedback | Structured feedback based on answer length |
| Resume improvement | Returns original content unchanged |

---

## Security Features

- ✅ Passwords hashed with PBKDF2 (Werkzeug `generate_password_hash`)
- ✅ Secure session cookies (`HttpOnly`, `SameSite=Lax`; `Secure=True` in production)
- ✅ Parameterised SQL queries (no SQL injection)
- ✅ Input validation on all forms
- ✅ Role-based access control (admin routes protected by decorator)
- ✅ AI API keys read from environment variables only — never in source or frontend code
- ✅ Admin credentials configurable via environment variables
- ✅ Safe output rendering via Jinja2 auto-escaping
- ✅ `SESSION_COOKIE_SECURE = True` in `ProductionConfig`
- ✅ ProxyFix applied only when `PROXY_COUNT > 0` (no unconditional IP spoofing risk)
- ✅ `PREFERRED_URL_SCHEME = 'https'` in production so `url_for()` generates correct URLs

---

## Deployment

### Local Development

```bash
FLASK_ENV=development python app.py
```

Open your browser at **http://localhost:5000**

---

### Why `10.214.198.49` cannot have a public HTTPS certificate

`10.214.198.49` is a **private network IP** — it is only reachable on your local Wi-Fi and is
invisible to the internet. Certificate authorities issue trusted TLS certificates only for
**public domain names** that resolve to a **publicly routable IP address**. The deployment
steps below move the application to a hosting platform that provides both.

---

### Option A — Render (recommended — free tier, automatic HTTPS)

Render is a managed cloud platform that:

- Runs Gunicorn directly — no server to manage
- Issues and auto-renews a Let's Encrypt TLS certificate
- Provides a public `https://your-app.onrender.com` URL immediately
- Handles HTTP-to-HTTPS redirection at the platform layer

#### Step 1 — Publish the code to GitHub

You must push the project to GitHub before Render can deploy it.

```bash
# In your project folder (CareerPathAI)
git init                          # skip if already a git repo
git add .
git commit -m "Initial commit"

# Create a new repository on github.com, then:
git remote add origin https://github.com/YOUR_USERNAME/careerpath-ai.git
git branch -M main
git push -u origin main
```

> **Before pushing**, confirm `.env` and `careerpath.db` are NOT tracked:
>
> ```bash
> git status   # neither .env nor careerpath.db should appear in the output
> ```
>
> Both are already listed in `.gitignore`.

#### Step 2 — Create a Render account and Web Service

1. Go to **https://render.com** and sign up (free).
2. Click **New → Web Service**.
3. Connect your GitHub account when prompted and select the `careerpath-ai` repository.
4. Confirm these settings in the Render form:

   | Setting | Value |
   |---|---|
   | **Name** | `careerpath-ai` (or any name you choose) |
   | **Region** | closest to your users |
   | **Branch** | `main` |
   | **Runtime** | `Python 3` |
   | **Build Command** | `pip install -r requirements.txt` |
   | **Start Command** | `gunicorn -c gunicorn.conf.py wsgi:app` |
   | **Plan** | Free |

#### Step 3 — Set environment variables

In the **Environment** section of the Render dashboard, add each variable below.
**Never paste real secrets into `render.yaml` or any file you commit to GitHub.**

| Variable | Value to set |
|---|---|
| `FLASK_ENV` | `production` |
| `SECRET_KEY` | run `python -c "import secrets; print(secrets.token_hex(32))"` locally and paste the output |
| `DATABASE_PATH` | `/tmp/careerpath.db` (free tier — see persistence note below) |
| `ADMIN_USERNAME` | your chosen admin username |
| `ADMIN_EMAIL` | your admin email address |
| `ADMIN_PASSWORD` | a strong password (min 12 characters) |
| `PROXY_COUNT` | `1` |
| `FORWARDED_ALLOW_IPS` | `*` |
| `AI_API_KEY` | your OpenAI key, or leave blank for demo mode |

> **Database persistence on the free tier:**
> Render's free tier does not provide a persistent disk. The SQLite file at `/tmp/careerpath.db`
> is reset every time the service redeploys or is restarted. For a demo or portfolio this is acceptable.
> To keep data permanently: upgrade to the **Starter plan ($7/mo)**, add a **Disk**
> (Render dashboard → your service → Disks → Add Disk, mount path `/data`), then set
> `DATABASE_PATH=/data/careerpath.db`.

#### Step 4 — Deploy

Click **Create Web Service**. Render will:

1. Clone your repository
2. Run `pip install -r requirements.txt`
3. Start `gunicorn -c gunicorn.conf.py wsgi:app`
4. Issue a TLS certificate for `your-app-name.onrender.com`
5. Mark the service **Live** once `/health` returns `200`

The first deploy takes about 2–4 minutes. Watch the build log in the dashboard.

#### Step 5 — Verify the deployment

Once Render shows **Live**, open the **Logs** tab and confirm you see lines like:

```
[INFO] Starting gunicorn
[INFO] Listening at: http://0.0.0.0:10000
[INFO] Booting worker with pid: ...
```

Then run these checks — replace the hostname with your actual Render URL:

```bash
# 1. Health endpoint — must return {"status": "ok", "database": "ok"}
curl https://careerpath-ai.onrender.com/health

# 2. Home page returns HTTP 200
curl -s -o /dev/null -w "%{http_code}" https://careerpath-ai.onrender.com/

# 3. HTTP redirects to HTTPS (Render enforces this at platform level)
curl -I http://careerpath-ai.onrender.com/
# Expected first line: HTTP/1.1 301 Moved Permanently

# 4. Certificate is valid — curl must NOT report a certificate error
curl -v https://careerpath-ai.onrender.com/ 2>&1 | grep -i "SSL\|issuer\|expire\|verify"
```

Only when all four checks pass is HTTPS confirmed working with a trusted certificate.

#### Step 6 — Optional: add a custom domain

1. Render dashboard → your service → **Settings → Custom Domains → Add Custom Domain**
2. Enter your domain (e.g. `careerpath-ai.com`)
3. Render shows a CNAME target (e.g. `careerpath-ai.onrender.com`)
4. In your DNS registrar's control panel, add:

   | Record type | Name | Value |
   |---|---|---|
   | CNAME | `www` | the Render hostname shown |
   | ALIAS or ANAME | `@` | the Render hostname (root domain — if your registrar supports ALIAS) |

5. Render issues a new TLS certificate for your custom domain automatically (1–5 minutes after DNS propagates).

> Do **not** point DNS at `10.214.198.49` — that is your local machine's private IP,
> unreachable from the public internet.

#### Post-deployment checklist

- [ ] `https://your-app.onrender.com/health` returns `{"status":"ok","database":"ok"}`
- [ ] Browser shows a padlock — no certificate warnings
- [ ] `http://` URL redirects to `https://` automatically
- [ ] Registration creates a new account successfully
- [ ] Login and logout work
- [ ] Dashboard loads after login and shows the correct username
- [ ] Career recommendations return results (demo or with API key)
- [ ] Admin panel at `/admin` is accessible with the `ADMIN_USERNAME`/`ADMIN_PASSWORD` you set
- [ ] `.env` and `careerpath.db` do **not** appear in `git log` or on GitHub

#### Tests that cannot run on Render directly

| Test | Reason | How to check instead |
|---|---|---|
| Full automated test suite | No pytest runner on Render | Run `python -m pytest tests/ -v` locally before each push |
| AI API response quality | Requires a real API key | Set `AI_API_KEY` in Render env vars, then test interview feedback and recommendations manually |
| Database persistence across restarts | Free tier resets on redeploy | Upgrade to Starter plan + Disk |

#### Continuous deployment

Every `git push origin main` triggers an automatic redeploy on Render.
To deploy manually: Render dashboard → your service → **Manual Deploy → Deploy latest commit**.

---

### Option B — VPS or dedicated server with Nginx + Let's Encrypt

Use this option if you manage your own Linux server (Ubuntu/Debian).

#### Architecture

```
Browser :443 (HTTPS)
    │
    ▼
Nginx (TLS termination, HTTP→HTTPS redirect)
    │ localhost:8000
    ▼
Gunicorn (WSGI, sync workers)
    │
    ▼
Flask app (wsgi.py → app.py)
    │
    ▼
SQLite (persistent volume path via DATABASE_PATH)
```

#### Step 1 — Point DNS to your server

In your domain registrar's DNS panel, add:

| Type | Name | Value |
|---|---|---|
| A | `@` | `<your server's public IPv4>` |
| A | `www` | `<your server's public IPv4>` |

Wait for propagation (usually a few minutes; up to 48 h). Verify:

```bash
dig +short yourdomain.com
# Should return your server's public IP
```

#### Step 2 — Install Nginx and Certbot

```bash
sudo apt update
sudo apt install -y nginx certbot python3-certbot-nginx
```

#### Step 3 — Deploy the application

```bash
git clone https://github.com/yourusername/careerpath-ai.git /opt/careerpath-ai
cd /opt/careerpath-ai
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env — set SECRET_KEY, ADMIN_PASSWORD, FLASK_ENV=production,
# DATABASE_PATH=/data/careerpath.db, PROXY_COUNT=1, FORWARDED_ALLOW_IPS=127.0.0.1
nano .env
```

#### Step 4 — Create a systemd service

Create `/etc/systemd/system/careerpath-ai.service`:

```ini
[Unit]
Description=CareerPath AI (Gunicorn)
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/careerpath-ai
EnvironmentFile=/opt/careerpath-ai/.env
ExecStart=/opt/careerpath-ai/venv/bin/gunicorn -c gunicorn.conf.py wsgi:app
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now careerpath-ai
sudo systemctl status careerpath-ai
```

#### Step 5 — Configure Nginx

```bash
sudo cp /opt/careerpath-ai/nginx.conf.example /etc/nginx/sites-available/careerpath-ai
# Edit the file — replace yourdomain.com and the static/ alias path
sudo nano /etc/nginx/sites-available/careerpath-ai

sudo ln -s /etc/nginx/sites-available/careerpath-ai /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### Step 6 — Obtain the Let's Encrypt certificate

```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

#### Step 7 — Verify

```bash
curl https://yourdomain.com/health
curl -I http://yourdomain.com/     # expect: 301
curl -sI https://yourdomain.com/ | grep -i strict
```

---

### Option C — Heroku

```bash
heroku create careerpath-ai
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
heroku config:set ADMIN_PASSWORD=YourStrongAdminPassword1!
heroku config:set PROXY_COUNT=1
heroku config:set FORWARDED_ALLOW_IPS="*"
heroku config:set AI_API_KEY=your-api-key   # optional

git push heroku main
```

> **Note:** Heroku's ephemeral filesystem means `careerpath.db` is reset on every dyno restart.  
> For persistent data, attach a Postgres add-on and update the database layer, or use an external SQLite volume.

---

### Option D — PythonAnywhere

PythonAnywhere provides HTTPS automatically for `.pythonanywhere.com` subdomains and for custom domains on paid plans.

1. Upload project files (or clone from Git in a Bash console)
2. Create a virtual environment and run `pip install -r requirements.txt`
3. In the **Web** tab, set the WSGI file to:

```python
import sys, os
sys.path.insert(0, '/home/<username>/careerpath-ai')
os.environ.setdefault('FLASK_ENV', 'production')
from wsgi import app as application
```

4. Set the working directory to your project folder and reload the web app.

> PythonAnywhere serves through its own proxy, so set `PROXY_COUNT=1` in a `.env` file on the server.

---

## DNS Configuration Reference

| Record type | Name | Value | Purpose |
|---|---|---|---|
| A | `@` | `<server public IP>` | Root domain → server |
| A | `www` | `<server public IP>` | www subdomain → server |
| CNAME | `www` | `<platform hostname>` | www → managed platform (alternative) |

**Important:** Do not set DNS to a private IP (`10.x.x.x`, `192.168.x.x`, etc.). Those addresses are not reachable from the public internet.

---

## Gunicorn Quick Reference

```bash
# Run with config file (recommended)
gunicorn -c gunicorn.conf.py wsgi:app

# Run inline (useful for quick checks on a VPS)
gunicorn -w 3 -b 127.0.0.1:8000 --timeout 60 wsgi:app

# Check Gunicorn is running locally
curl http://127.0.0.1:8000/health
```

| Flag | Purpose |
|---|---|
| `-c gunicorn.conf.py` | Load settings from config file |
| `-w 3` | 3 worker processes (`2 × CPU + 1` is the guide) |
| `-b 127.0.0.1:8000` | Bind to localhost (Nginx sits in front) |
| `--timeout 60` | Worker timeout (increase for slow AI calls) |
| `--access-logfile -` | Log access to stdout |

---

## Production Checklist

- [ ] `SECRET_KEY` is randomly generated — not the default string
- [ ] `ADMIN_PASSWORD` is changed from the default
- [ ] `FLASK_ENV=production` is set
- [ ] Application starts with `gunicorn -c gunicorn.conf.py wsgi:app`, not `python app.py`
- [ ] `PROXY_COUNT=1` and `FORWARDED_ALLOW_IPS` are set (if behind a proxy)
- [ ] Domain resolves to a **public** IP, not a private IP like `10.214.198.49`
- [ ] HTTPS certificate is issued by a trusted CA for your domain name
- [ ] `/health` endpoint returns `{"status": "ok", "database": "ok"}`
- [ ] HTTP URL redirects to HTTPS automatically
- [ ] Browser shows a padlock — no certificate warnings
- [ ] `DATABASE_PATH` points to a persistent volume
- [ ] `.env` is **not** committed to version control
- [ ] `AI_API_KEY` is set (or demo mode is intentional)

---

## Health Check

The `/health` endpoint is available without authentication and returns JSON:

```json
{"status": "ok", "database": "ok"}
```

Returns HTTP `200` when healthy, `503` when the database is unreachable.  
Use this URL with uptime monitors (UptimeRobot, Render health checks, Kubernetes probes, etc.).

---

## Career Paths Covered

1. Software Developer
2. Data Analyst
3. AI/ML Engineer
4. Web Developer
5. Cybersecurity Analyst
6. Cloud Engineer
7. UI/UX Designer
8. Digital Marketing Specialist

---

## SDG 8 Alignment

CareerPath AI directly supports **UN Sustainable Development Goal 8: Decent Work and Economic Growth** by:

- Bridging the gap between education and employment
- Helping students identify and develop market-relevant skills
- Providing free, accessible career guidance for all backgrounds
- Supporting entrepreneurship through practical project recommendations
- Preparing students for job interviews and professional resume writing

---

## Disclaimer

Career recommendations are provided for educational guidance purposes only.
They do not guarantee employment or accurately predict career success.
Career requirements vary by employer, location, and industry.
Sample interview answers are examples for learning, not model answers.

---

## Licence

This project was created as a college assignment. Free to use for educational purposes.
