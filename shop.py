from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from extensions import db
from models import Shop, Order
import json

shop_bp = Blueprint('shop', __name__, url_prefix='/shop')


# -------------------
# SHOP AUTH DECORATOR
# -------------------
def shop_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'shop_id' not in session:
            return redirect(url_for('shop.shop_login'))
        return f(*args, **kwargs)
    return decorated


# -------------------
# SHOP REGISTER
# -------------------
@shop_bp.route('/register', methods=['GET', 'POST'])
def shop_register():
    if request.method == 'POST':
        shop_name     = request.form.get('shop_name', '').strip()
        owner_name    = request.form.get('owner_name', '').strip()
        email         = request.form.get('email', '').strip()
        phone         = request.form.get('phone', '').strip()
        address       = request.form.get('address', '').strip()
        city          = request.form.get('city', '').strip()
        pincode       = request.form.get('pincode', '').strip()
        license_number = request.form.get('license_number', '').strip()
        password      = request.form.get('password', '')
        confirm_pass  = request.form.get('confirm_password', '')

        if not all([shop_name, owner_name, email, phone, password]):
            return render_template('shop/register.html', error='Please fill all required fields.')

        if password != confirm_pass:
            return render_template('shop/register.html', error='Passwords do not match.')

        if Shop.query.filter_by(email=email).first():
            return render_template('shop/register.html', error='Email already registered.')

        shop = Shop(
            shop_name=shop_name,
            owner_name=owner_name,
            email=email,
            phone=phone,
            address=address,
            city=city,
            pincode=pincode,
            license_number=license_number,
            password=generate_password_hash(password),
            is_approved=False
        )
        db.session.add(shop)
        db.session.commit()

        return render_template('shop/register.html',
            success='Registration submitted! Wait for admin approval before logging in.')

    return render_template('shop/register.html')


# -------------------
# SHOP LOGIN
# -------------------
@shop_bp.route('/login', methods=['GET', 'POST'])
def shop_login():
    if request.method == 'POST':
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        shop = Shop.query.filter_by(email=email).first()

        if not shop:
            return render_template('shop/login.html', error='No shop found with this email.')

        if not check_password_hash(shop.password, password):
            return render_template('shop/login.html', error='Wrong password.')

        if not shop.is_approved:
            return render_template('shop/login.html',
                error='Your shop is not approved yet. Please wait for admin approval.')

        session['shop_id'] = shop.id
        session['shop_name'] = shop.shop_name
        return redirect(url_for('shop.dashboard'))

    return render_template('shop/login.html')


# -------------------
# SHOP DASHBOARD
# -------------------
@shop_bp.route('/dashboard')
@shop_required
def dashboard():
    shop = Shop.query.get(session['shop_id'])
    orders = Order.query.filter_by(shop_id=shop.id).order_by(Order.id.desc()).all()

    parsed_orders = []
    for o in orders:
        try:
            items = json.loads(o.items) if o.items else []
        except Exception:
            items = []
        parsed_orders.append({
            'id': o.id,
            'items': items,
            'name': o.name,
            'phone': o.phone,
            'address': o.address,
            'city': o.city,
            'pincode': o.pincode,
            'payment': o.payment,
            'total_price': o.total_price or 0,
            'status': o.status,
            'shop_status': o.shop_status or 'Pending',
            'suggestion': o.suggestion or '',
            'created_at': o.created_at.strftime('%d %b %Y, %I:%M %p') if o.created_at else ''
        })

    # Count stats
    total = len(parsed_orders)
    pending = sum(1 for o in parsed_orders if o['shop_status'] == 'Pending')
    accepted = sum(1 for o in parsed_orders if o['shop_status'] == 'Accepted')
    rejected = sum(1 for o in parsed_orders if o['shop_status'] == 'Rejected')
    revenue = sum(o['total_price'] for o in parsed_orders if o['shop_status'] == 'Accepted')

    return render_template('shop/dashboard.html',
        shop=shop,
        orders=parsed_orders,
        total=total,
        pending=pending,
        accepted=accepted,
        rejected=rejected,
        revenue=revenue
    )


# -------------------
# ACCEPT / REJECT ORDER (called from popup)
# -------------------
@shop_bp.route('/order/<int:order_id>/action', methods=['POST'])
@shop_required
def order_action(order_id):
    order = Order.query.get_or_404(order_id)

    # Make sure this order belongs to this shop
    if order.shop_id != session['shop_id']:
        return jsonify({'error': 'Unauthorized'}), 403

    action = request.form.get('action')  # 'accept' or 'reject'

    if action == 'accept':
        order.shop_status = 'Accepted'
        order.status = 'Confirmed'
    elif action == 'reject':
        order.shop_status = 'Rejected'
        order.status = 'Cancelled'

    db.session.commit()
    return redirect(url_for('shop.dashboard'))


# -------------------
# POLL FOR NEW ORDERS (used by JS notification system)
# -------------------
@shop_bp.route('/new_orders_count')
@shop_required
def new_orders_count():
    shop_id = session['shop_id']
    count = Order.query.filter_by(shop_id=shop_id, shop_status='Pending').count()

    # Get the latest pending orders for popup
    pending_orders = Order.query.filter_by(
        shop_id=shop_id, shop_status='Pending'
    ).order_by(Order.id.desc()).limit(5).all()

    orders_data = []
    for o in pending_orders:
        try:
            items = json.loads(o.items) if o.items else []
        except Exception:
            items = []
        orders_data.append({
            'id': o.id,
            'name': o.name,
            'phone': o.phone,
            'total_price': o.total_price,
            'items': items,
            'created_at': o.created_at.strftime('%I:%M %p') if o.created_at else ''
        })

    return jsonify({'count': count, 'orders': orders_data})


# -------------------
# SHOP PROFILE
# -------------------
@shop_bp.route('/profile')
@shop_required
def profile():
    shop = Shop.query.get(session['shop_id'])
    return render_template('shop/profile.html', shop=shop)


# -------------------
# SHOP LOGOUT
# -------------------
@shop_bp.route('/logout')
def shop_logout():
    session.pop('shop_id', None)
    session.pop('shop_name', None)
    return redirect(url_for('shop.shop_login'))