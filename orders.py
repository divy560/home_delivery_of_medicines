from flask import Blueprint, render_template, request, redirect, url_for, session
from extensions import db
from models import Medicine, Order, UserMedicine
import json

orders_bp = Blueprint('orders', __name__)


@orders_bp.route('/medicine/<int:medicine_id>')
def medicine_detail(medicine_id):
    med = Medicine.query.get(medicine_id)
    if not med:
        return "Medicine not found", 404
    return render_template('medicine_detail.html', med=med)


@orders_bp.route('/add_medicine', methods=['POST'])
def add_medicine():
    name = request.form['name']
    price = float(request.form['price'])
    category = request.form.get('category', '')
    new_med = Medicine(name=name, price=price, category=category)
    db.session.add(new_med)
    db.session.commit()
    return redirect(url_for('orders.medicine_detail', medicine_id=new_med.id))


# FIX: "Buy Now" adds item to cart then redirects to checkout — does NOT skip checkout
@orders_bp.route('/confirm_order/<int:medicine_id>', methods=['GET', 'POST'])
def confirm_order(medicine_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    med = Medicine.query.get(medicine_id)
    if not med:
        return "Medicine not found", 404

    # Add to cart with quantity 1, then go to checkout
    cart = session.get('cart', [])
    for item in cart:
        if item['id'] == medicine_id:
            item['quantity'] += 1
            break
    else:
        cart.append({'id': medicine_id, 'quantity': 1})

    session['cart'] = cart
    session.modified = True

    return redirect(url_for('checkout'))


# FIX: my_orders — properly parses items JSON and passes structured data to template
@orders_bp.route('/my_orders')
def my_orders():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    raw_orders = Order.query.filter_by(
        user_id=session['user_id']
    ).order_by(Order.id.desc()).all()

    parsed_orders = []
    for order in raw_orders:
        try:
            items = json.loads(order.items) if order.items else []
        except Exception:
            items = []

        parsed_orders.append({
            'id': order.id,
            'items': items,
            'total_price': order.total_price or 0,
            'status': order.status or 'Pending',
            'payment': order.payment or 'COD',
            'address': order.address or '',
            'city': order.city or '',
            'pincode': order.pincode or '',
            'suggestion': order.suggestion or ''
        })

    return render_template('my_orders.html', orders=parsed_orders)