from flask import Blueprint, render_template
import csv
import os

medicines_bp = Blueprint('medicines', __name__)


@medicines_bp.route('/medicines/popular/<int:page>')
def popular_medicines(page):
    file_path = os.path.join('data', 'popular_medicines.csv')

    medicines_list = []

    if os.path.exists(file_path):
        with open(file_path, newline="") as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if len(row) == 2:
                    name, price = row
                    medicines_list.append({"name": name, "price": price})

    return render_template('popular_medicines.html', medicines=medicines_list)