from extensions import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    password = db.Column(db.String(200))
    is_admin = db.Column(db.Boolean, default=False)


class Shop(db.Model):
    __tablename__ = 'shop'
    id = db.Column(db.Integer, primary_key=True)
    shop_name = db.Column(db.String(150))
    owner_name = db.Column(db.String(100))
    email = db.Column(db.String(150), unique=True)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    city = db.Column(db.String(100))
    pincode = db.Column(db.String(20))
    license_number = db.Column(db.String(100))
    password = db.Column(db.String(200))
    is_approved = db.Column(db.Boolean, default=False)
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
    orders = db.relationship('Order', backref='shop', foreign_keys='Order.shop_id',
                              primaryjoin='Shop.id == Order.shop_id', lazy=True)


class Medicine(db.Model):
    __tablename__ = 'medicine'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    category = db.Column(db.String(100))
    price = db.Column(db.Float)
    is_popular = db.Column(db.Boolean, default=False)


class Order(db.Model):
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    shop_id = db.Column(db.Integer, db.ForeignKey('shop.id'), nullable=True)
    items = db.Column(db.Text)
    name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    city = db.Column(db.String(100))
    pincode = db.Column(db.String(20))
    payment = db.Column(db.String(20))
    suggestion = db.Column(db.Text)
    total_price = db.Column(db.Float)
    status = db.Column(db.String(50), default='Pending')
    shop_status = db.Column(db.String(50), default='Pending')  # shop accepts/rejects
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='orders', foreign_keys=[user_id])


class Contact(db.Model):
    __tablename__ = 'contact'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(150))
    phone = db.Column(db.String(20))
    message = db.Column(db.Text)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)


class UserMedicine(db.Model):
    __tablename__ = 'user_medicine'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    medicine_id = db.Column(db.Integer, db.ForeignKey('medicine.id'))
    times_ordered = db.Column(db.Integer, default=1)

   