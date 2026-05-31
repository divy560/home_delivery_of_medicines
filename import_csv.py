"""
Run this whenever you update your CSV file:
    python import_csv.py

It will:
- Add new medicines that don't exist yet
- Update price/category/popular status of existing medicines
- Never create duplicates
"""

import csv
from app import app
from extensions import db
from models import Medicine

CSV_FILE = 'data/medicines.csv'   # change to your CSV path if different

with app.app_context():
    added = 0
    updated = 0
    skipped = 0

    with open(CSV_FILE, newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)

        for row in reader:
            name = row['name'].strip()
            category = row.get('category', '').strip()
            price = float(row['price'])
            is_popular = row.get('is_popular', 'False').strip().lower() == 'true'

            # Check if medicine already exists by name
            existing = Medicine.query.filter_by(name=name).first()

            if existing:
                # Update existing medicine with new values from CSV
                existing.category = category
                existing.price = price
                existing.is_popular = is_popular
                updated += 1
            else:
                # Add new medicine
                med = Medicine(
                    name=name,
                    category=category,
                    price=price,
                    is_popular=is_popular
                )
                db.session.add(med)
                added += 1

    db.session.commit()

    print(f"\n✅ CSV import complete!")
    print(f"   ➕ Added:   {added} new medicines")
    print(f"   🔄 Updated: {updated} existing medicines")
    print(f"   📦 Total in DB: {Medicine.query.count()}")