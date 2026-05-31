from app import app
from extensions import db
from models import User, Medicine, Order, UserMedicine

with app.app_context():
    db.drop_all()
    db.create_all()

    print("Database created successfully 🚀")