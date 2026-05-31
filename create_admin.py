"""
Run this once to create your admin account:
    python create_admin.py
"""
from app import app
from extensions import db
from models import User
from werkzeug.security import generate_password_hash

ADMIN_USERNAME = "divyansh21"
ADMIN_PASSWORD = "12345"   

with app.app_context():
    existing = User.query.filter_by(username=ADMIN_USERNAME).first()
    if existing:
        existing.is_admin = True
        existing.password = generate_password_hash(ADMIN_PASSWORD)
        db.session.commit()
        print(f"✅ Updated existing user '{ADMIN_USERNAME}' to admin.")
    else:
        user = User(
            username=ADMIN_USERNAME,
            password=generate_password_hash(ADMIN_PASSWORD),
            is_admin=True
        )
        db.session.add(user)
        db.session.commit()
        print(f"✅ Admin account created!")

    print(f"   Username: {ADMIN_USERNAME}")
    print(f"   Password: {ADMIN_PASSWORD}")
    print(f"   Login at: http://127.0.0.1:5000/admin/login")