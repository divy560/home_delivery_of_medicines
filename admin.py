from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from functools import wraps
from extensions import db
from models import User, Order, Medicine, Contact, Shop
import json

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


# -------------------
# ADMIN AUTH DECORATOR
# -------------------
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        user = User.query.get(session['user_id'])
        if not user or not user.is_admin:
            return render_template('admin/unauthorized.html'), 403
        return f(*args, **kwargs)
    return decorated


# -------------------
# ADMIN LOGIN (separate from user login)
# -------------------
@admin_bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        from werkzeug.security import check_password_hash
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password) and user.is_admin:
            session['user_id'] = user.id
            session['is_admin'] = True
            return redirect(url_for('admin.dashboard'))
        else:
            return render_template('admin/login.html', error="Invalid credentials or not an admin.")

    return render_template('admin/login.html')


# -------------------
# DASHBOARD
# -------------------
@admin_bp.route('/')
@admin_required
def dashboard():
    total_orders = Order.query.count()
    pending = Order.query.filter_by(status='Pending').count()
    delivered = Order.query.filter_by(status='Delivered').count()
    total_revenue = db.session.query(db.func.sum(Order.total_price)).scalar() or 0
    total_users = User.query.filter_by(is_admin=False).count()
    total_medicines = Medicine.query.count()
    contacts = Contact.query.count()
    recent_orders = Order.query.order_by(Order.id.desc()).limit(5).all()

    return render_template('admin/dashboard.html',
        total_orders=total_orders,
        pending=pending,
        delivered=delivered,
        total_revenue=total_revenue,
        total_users=total_users,
        total_medicines=total_medicines,
        contacts=contacts,
        recent_orders=recent_orders
    )


# -------------------
# ALL ORDERS
# -------------------
@admin_bp.route('/orders')
@admin_required
def orders():
    status_filter = request.args.get('status', '')
    if status_filter:
        all_orders = Order.query.filter_by(status=status_filter).order_by(Order.id.desc()).all()
    else:
        all_orders = Order.query.order_by(Order.id.desc()).all()

    parsed = []
    for o in all_orders:
        try:
            items = json.loads(o.items) if o.items else []
        except Exception:
            items = []
        parsed.append({
            "order": o,
            "items": items
        })

    return render_template('admin/orders.html', orders=parsed, status_filter=status_filter)


# -------------------
# UPDATE ORDER STATUS
# -------------------
@admin_bp.route('/orders/<int:order_id>/update_status', methods=['POST'])
@admin_required
def update_status(order_id):
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get('status')
    if new_status in ['Pending', 'Confirmed', 'Out for Delivery', 'Delivered', 'Cancelled']:
        order.status = new_status
        db.session.commit()
    return redirect(url_for('admin.orders'))


# -------------------
# ORDER DETAIL
# -------------------
@admin_bp.route('/orders/<int:order_id>')
@admin_required
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    try:
        items = json.loads(order.items) if order.items else []
    except Exception:
        items = []
    return render_template('admin/order_detail.html', order=order, items=items)


# -------------------
# SUGGESTIONS (from orders)
# -------------------
@admin_bp.route('/suggestions')
@admin_required
def suggestions():
    orders_with_suggestions = Order.query.filter(
        Order.suggestion != None,
        Order.suggestion != ''
    ).order_by(Order.id.desc()).all()
    return render_template('admin/suggestions.html', orders=orders_with_suggestions)


# -------------------
# CONTACTS
# -------------------
@admin_bp.route('/contacts')
@admin_required
def contacts():
    all_contacts = Contact.query.order_by(Contact.id.desc()).all()
    return render_template('admin/contacts.html', contacts=all_contacts)


# -------------------
# USERS
# -------------------
@admin_bp.route('/users')
@admin_required
def users():
    all_users = User.query.filter_by(is_admin=False).order_by(User.id.desc()).all()
    return render_template('admin/users.html', users=all_users)


# -------------------
# MEDICINES
# -------------------
@admin_bp.route('/medicines')
@admin_required
def medicines():
    all_meds = Medicine.query.order_by(Medicine.id.desc()).all()
    return render_template('admin/medicines.html', medicines=all_meds)


@admin_bp.route('/medicines/add', methods=['POST'])
@admin_required
def add_medicine():
    name = request.form.get('name')
    category = request.form.get('category')
    price = float(request.form.get('price', 0))
    is_popular = request.form.get('is_popular') == 'on'
    med = Medicine(name=name, category=category, price=price, is_popular=is_popular)
    db.session.add(med)
    db.session.commit()
    return redirect(url_for('admin.medicines'))


@admin_bp.route('/medicines/<int:med_id>/delete', methods=['POST'])
@admin_required
def delete_medicine(med_id):
    med = Medicine.query.get_or_404(med_id)
    db.session.delete(med)
    db.session.commit()
    return redirect(url_for('admin.medicines'))


# -------------------
# SHOPS
# -------------------
@admin_bp.route('/shops')
@admin_required
def shops():
    status_filter = request.args.get('status', '')
    if status_filter == 'pending':
        all_shops = Shop.query.filter_by(is_approved=False).order_by(Shop.id.desc()).all()
    elif status_filter == 'approved':
        all_shops = Shop.query.filter_by(is_approved=True).order_by(Shop.id.desc()).all()
    else:
        all_shops = Shop.query.order_by(Shop.id.desc()).all()
    return render_template('admin/shops.html', shops=all_shops, status_filter=status_filter)


@admin_bp.route('/shops/<int:shop_id>/approve', methods=['POST'])
@admin_required
def approve_shop(shop_id):
    shop = Shop.query.get_or_404(shop_id)
    shop.is_approved = True
    db.session.commit()
    return redirect(url_for('admin.shops'))


@admin_bp.route('/shops/<int:shop_id>/delete', methods=['POST'])
@admin_required
def delete_shop(shop_id):
    shop = Shop.query.get_or_404(shop_id)
    db.session.delete(shop)
    db.session.commit()
    return redirect(url_for('admin.shops'))


# -------------------
# ADMIN LOGOUT
# -------------------
@admin_bp.route('/logout')
def admin_logout():
    session.pop('user_id', None)
    session.pop('is_admin', None)
    return redirect(url_for('admin.admin_login'))