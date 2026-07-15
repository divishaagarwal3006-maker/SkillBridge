# SkillBridge

A working starter version of SkillBridge — a platform matching students with
small real tasks posted by companies, so students earn proof of skill
(ratings + certificates) instead of just a degree.
🔗 **Live demo:** https://skillbridge-4cby.onrender.com

**Stack:** Python (Flask) backend · SQLite database · HTML/CSS/JS frontend.

## Features included
- Student & company signup/login (separate account types)
- Companies can post tasks (title, description, required skill, payment)
- Students browse/filter tasks by skill, with "matches your skills" highlighting
- Students apply to tasks
- Companies accept/reject applicants, then rate completed work
- Student profile auto-tracks average rating from completed tasks
- Responsive, dark-navy themed UI matching the original pitch deck

## Setup

1. **Install Python** (3.9+) if you don't have it already.

2. **Create a virtual environment** (recommended):
```bash
   python -m venv venv
   venv\Scripts\activate      # Windows
   source venv/bin/activate   # Mac/Linux
```

3. **Install dependencies:**
```bash
   pip install -r requirements.txt
```

4. **(Optional) Seed some demo data:**
```bash
   python seed.py
```
   This creates 2 demo companies with 4 tasks, and 1 demo student
   (login: `divisha@example.com` / `password123`).

5. **Run the app:**
```bash
   python app.py
```

6. Open **http://127.0.0.1:5000** in your browser.

   <img width="1885" height="1006" alt="image" src="https://github.com/user-attachments/assets/a32cc0ca-08d2-4c9d-8727-6f668e74b606" />


## Project structure
skillbridge/
├── app.py                  # Flask app: routes, models, matching logic
├── seed.py                 # Optional demo-data script
├── requirements.txt
├── templates/               # Jinja2 HTML templates
│   ├── base.html
│   ├── index.html
│   ├── student_signup.html
│   ├── company_signup.html
│   ├── login.html
│   ├── tasks.html
│   ├── task_detail.html
│   ├── post_task.html
│   ├── student_dashboard.html
│   └── company_dashboard.html
└── static/
└── css/style.css        # All styling

## How the skill matching works
A simple exact-match check (case-insensitive) between a student's listed
skills and a task's required skill. This mirrors the "Skill-based task
matching algorithm" concept, implemented in Python. Extendable later for
partial matches, synonyms, or weighted scoring.

## 🚀 Future Improvements
- In-app chat between student and company
- Skill badges (Gold, Silver, Bronze tiers) based on ratings
- Public leaderboard and student portfolio showcase
- File upload for task submissions instead of text notes
- AI-powered task recommendations for students
- Certificate generation (PDF) for highly rated work
- Payment gateway integration for paid tasks
- Mobile app version (iOS & Android)
- Deploy backend on Render/Railway (GitHub Pages can't run Python)
