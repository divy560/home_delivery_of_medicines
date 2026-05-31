import csv
from extensions import db
from models import Medicine
from app import app

csv_file = "data/popular_medicines.csv"

with app.app_context():
    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            category = row.get("category", "")
            price = float(row["price"])
            is_popular = row["is_popular"].lower() == "true"

            existing = Medicine.query.filter_by(name=name).first()
            if not existing:
                med = Medicine(name=name, category=category, price=price, is_popular=is_popular)
                db.session.add(med)
        db.session.commit()
        print("✅ Medicines imported successfully!")