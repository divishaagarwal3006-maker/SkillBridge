# SkillBridge

A working starter version of SkillBridge — a platform matching students with
small real tasks posted by companies, so students earn proof of skill
(ratings + certificates) instead of just a degree.

**Stack:** Python (Flask) backend · SQLite database · HTML/CSS/JS frontend.

## Frk-navy themed UI matching the original pitch deck

## Setup

1. Install Python (3.9+)
2. Create a virtual environment:

6. Open http://127.0.0.1:5000

## How the skill matching works
A simple exact-match check (case-insensitive) between a student's listed
skills and a task's required skill. Extendable later for partial matches
or weighted scoring.

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