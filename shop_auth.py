from flask import Blueprint, render_template, request, redirect, session, url_for
from extensions import db
from models import Shop
from werkzeug.security import generate_password_hash, check_password_hash

shop_auth_bp = Blueprint('shop_auth', __name__)

# -------------------
# SHOP REGISTER
# -------------------
@shop_auth_bp.route('/shop/register', methods=['GET', 'POST'])
def shop_register():
    if request.method == 'POST':
        shop_name = request.form['shop_name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        shop = Shop(shop_name=shop_name, email=email, password=password)
        db.session.add(shop)
        db.session.commit()

        return redirect(url_for('shop_auth.shop_login'))

    return render_template('shop_register.html')


# -------------------
# SHOP LOGIN
# -------------------
@shop_auth_bp.route('/shop/login', methods=['GET', 'POST'])
def shop_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        shop = Shop.query.filter_by(email=email).first()

        if shop and check_password_hash(shop.password, password):
            session['shop_id'] = shop.id
            return redirect('/shop/dashboard')

        return "Invalid credentials"

    return render_template('shop_login.html')


# -------------------
# SHOP DASHBOARD
# -------------------
@shop_auth_bp.route('/shop/dashboard')
def shop_dashboard():
    if 'shop_id' not in session:
        return redirect(url_for('shop_auth.shop_login'))

    return render_template("shop_dashboard.html")