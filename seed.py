"""
Optional: populate the database with a few demo companies, students,
and tasks so the site isn't empty on first run.

Run once with:  python seed.py
"""
from app import app, db, Student, Company, Task
from werkzeug.security import generate_password_hash

with app.app_context():
    db.create_all()

    if Company.query.count() == 0:
        c1 = Company(name="Northwind Studio", email="hello@northwind.dev",
                     password_hash=generate_password_hash("password123"),
                     about="A small design studio helping startups look sharp.")
        c2 = Company(name="Lumen Analytics", email="team@lumen.io",
                     password_hash=generate_password_hash("password123"),
                     about="Data-driven insights for small businesses.")
        db.session.add_all([c1, c2])
        db.session.commit()

        tasks = [
            Task(company_id=c1.id, title="Design a logo for our app",
                 description="We need a clean, modern logo for our new productivity app. Deliver as SVG + PNG.",
                 skill_required="Logo Design", payment=1500),
            Task(company_id=c1.id, title="Write 5 product landing-page headlines",
                 description="Short, punchy headlines for an A/B test on our homepage.",
                 skill_required="Content Writing", payment=500),
            Task(company_id=c2.id, title="Clean up a 2,000-row customer spreadsheet",
                 description="Remove duplicates, standardize phone numbers, and flag missing emails.",
                 skill_required="Data Entry", payment=800),
            Task(company_id=c2.id, title="Build a simple Python script to merge two CSVs",
                 description="Merge sales.csv and inventory.csv on product_id, output combined.csv.",
                 skill_required="Python", payment=1200),
        ]
        db.session.add_all(tasks)
        db.session.commit()
        print("Seeded companies and tasks.")

    if Student.query.count() == 0:
        s1 = Student(name="Divisha Agarwal", email="divisha@example.com",
                     password_hash=generate_password_hash("password123"),
                     skills="Python, Data Entry, Content Writing",
                     bio="B.Tech CS student interested in cybersecurity and AI.")
        db.session.add(s1)
        db.session.commit()
        print("Seeded a demo student (login: divisha@example.com / password123).")

    print("Done.")