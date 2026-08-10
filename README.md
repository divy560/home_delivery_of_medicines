# Home Delivery of Medicines

A web-based medicine delivery application built with Python Flask.
The application allows users to browse medicines, search for medicines,
add medicines to a cart, place orders, and track their orders.

It also includes an admin section for managing medicines, users, orders,
shops, and customer contacts.

## Features

### User Features

- User registration and login
- Secure password hashing
- Browse popular medicines
- Search for medicines
- Browse medicines by category
- View medicine details
- Add medicines to cart
- Increase or decrease cart quantity
- Remove medicines from cart
- Checkout and place orders
- View previous orders
- Order status tracking
- Doctor profile pages

### Admin Features

- Admin login
- Admin dashboard
- View total orders
- View pending and delivered orders
- View total revenue
- Manage users
- Manage medicines
- Add and delete medicines
- View customer contacts
- Manage registered shops
- Approve or delete shops
- Update order status
- View order details
- View customer suggestions

## Technologies Used

- Python
- Flask
- Flask-SQLAlchemy
- SQLite
- HTML
- CSS
- JavaScript
- Jinja2 Templates
- Gunicorn

## Database

The application uses SQLite with Flask-SQLAlchemy.

The database is configured as:

`sqlite:///test.db`

The application creates the database tables automatically when the application starts.

## Project Structure

```text
home_delivery_of_medicines/
│
├── app.py
├── auth.py
├── admin.py
├── cart.py
├── orders.py
├── medicines.py
├── models.py
├── extensions.py
├── config.py
│
├── create_admin.py
├── create_db.py
├── import_csv.py
├── load_medicines.py
│
├── data/
│   └── medicines.csv
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
├── templates/
│   ├── admin/
│   └── ...
│
├── requirements.txt
├── render.yaml
└── README.md
