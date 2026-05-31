from flask import Flask, render_template, session, request, jsonify, redirect, url_for, flash
from extensions import db
import json

app = Flask(__name__)
app.secret_key = "secret123"

# -------------------
# DB CONFIG
# -------------------
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# -------------------
# MODELS
# -------------------
from models import User, Medicine, Order, UserMedicine

# -------------------
# CART HELPER
# -------------------
def get_cart():
    if "cart" not in session:
        session["cart"] = []
    return session["cart"]

# -------------------
# USER CONTEXT
# -------------------
@app.context_processor
def inject_user():
    user = None
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
    return dict(user=user)

# -------------------
# BLUEPRINTS
# -------------------
from auth import auth_bp
from orders import orders_bp
from cart import cart_bp
from admin import admin_bp
from shop import shop_bp

app.register_blueprint(shop_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(orders_bp)
app.register_blueprint(cart_bp)

# -------------------
# HOME PAGE
# -------------------
@app.route('/')
def home():
    medicines = Medicine.query.filter_by(is_popular=True).limit(6).all()
    return render_template('home.html', medicines=medicines)

# -------------------
# DOCTORS
# -------------------
@app.route('/doctor/<int:id>')
def doctor_profile(id):
    doctors = {
        1: {"name": "Dr. Aman Verma", "special": "Cardiologist", "exp": "12+ years",
            "desc": "Heart specialist", "img": "https://cdn-icons-png.flaticon.com/512/3774/3774299.png"},
        2: {"name": "Dr. Neha Sharma", "special": "Dermatologist", "exp": "9+ years",
            "desc": "Skin specialist", "img": "https://cdn-icons-png.flaticon.com/512/3774/3774299.png"},
        3: {"name": "Dr. Raj Mehta", "special": "General Physician", "exp": "15+ years",
            "desc": "General health expert", "img": "https://cdn-icons-png.flaticon.com/512/3774/3774299.png"}
    }
    return render_template("doctor.html", doctor=doctors.get(id))

# -------------------
# SEARCH
# -------------------
@app.route('/search')
def search():
    query = request.args.get('q')
    if not query:
        return jsonify({"results": []})

    medicines = Medicine.query.filter(
        Medicine.name.ilike(f"%{query}%")
    ).all()

    return jsonify({
        "results": [
            {"id": m.id, "name": m.name, "price": m.price}
            for m in medicines
        ]
    })

# -------------------
# CATEGORY
# -------------------
@app.route('/category/<name>')
def category(name):
    medicines = Medicine.query.filter_by(category=name).all()
    return render_template('category.html', medicines=medicines, category=name)

# -------------------
# ADD TO CART (JSON API - called from JS)
# -------------------
@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    data = request.get_json()

    med_id = int(data.get('medicine_id'))
    qty = int(data.get('quantity', 1))

    cart = get_cart()

    for item in cart:
        if item["id"] == med_id:
            item["quantity"] += qty
            break
    else:
        cart.append({"id": med_id, "quantity": qty})

    session["cart"] = cart
    session.modified = True  # FIX: force session save
    return jsonify({"message": "Added to cart", "cart_count": len(cart)})

# -------------------
# CHECKOUT PAGE (only defined here, removed from orders.py)
# -------------------
@app.route('/checkout')
def checkout():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    cart = get_cart()

    if not cart:
        return redirect(url_for('cart.view_cart'))

    items = []
    total = 0

    for item in cart:
        med = Medicine.query.get(item["id"])
        if not med:
            continue

        subtotal = med.price * item["quantity"]

        items.append({
            "id": med.id,
            "name": med.name,
            "price": med.price,
            "quantity": item["quantity"],
            "total": subtotal
        })

        total += subtotal

    return render_template("checkout.html", cart_items=items, total=total)

# -------------------
# PLACE ORDER
# -------------------
@app.route('/place_order', methods=['POST'])
def place_order():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    cart = get_cart()

    if not cart:
        return redirect(url_for('cart.view_cart'))

    items = []
    total = 0

    for i in cart:
        med = Medicine.query.get(i["id"])
        if not med:
            continue

        items.append({
            "id": med.id,
            "name": med.name,
            "price": med.price,
            "quantity": i["quantity"]
        })

        total += med.price * i["quantity"]

    order = Order(
        user_id=session.get("user_id"),
        shop_id=1,
        items=json.dumps(items),

        name=request.form.get("name"),
        phone=request.form.get("phone"),
        address=request.form.get("address"),
        city=request.form.get("city"),
        pincode=request.form.get("pincode"),

        payment=request.form.get("payment"),
        suggestion=request.form.get("suggestion"),

        total_price=total,
        status="Pending"
    )

    db.session.add(order)
    db.session.commit()

    session["cart"] = []
    session.modified = True

    # FIX: redirect to a proper success page instead of returning plain text
    return redirect(url_for('order_success', order_id=order.id))

# -------------------
# ORDER SUCCESS PAGE
# -------------------
@app.route('/order_success/<int:order_id>')
def order_success(order_id):
    order = Order.query.get(order_id)
    return render_template("order_success.html", order=order)

# -------------------
# ADMIN ORDERS
# -------------------
@app.route('/admin/orders')
def admin_orders():
    orders = Order.query.order_by(Order.id.desc()).all()
    return render_template("admin_orders.html", orders=orders)

# -------------------
# SHOP ORDERS
# -------------------
@app.route('/shop/orders')
def shop_orders():
    if 'shop_id' not in session:
        return redirect('/shop/login')

    orders = Order.query.filter_by(shop_id=session['shop_id']).all()
    return render_template("shop_orders.html", orders=orders)

# -------------------
# DEBUG ROUTES
# -------------------
@app.route('/debug')
def debug():
    meds = Medicine.query.all()
    return jsonify([{"id": m.id, "name": m.name, "is_popular": m.is_popular} for m in meds])

@app.route('/check')
def check():
    meds = Medicine.query.all()
    return {"count": len(meds), "data": [{"name": m.name, "popular": m.is_popular} for m in meds]}

# -------------------
# CREATE TABLES + SEED DATA  (FIX: properly inside app context)
# -------------------
with app.app_context():
    db.create_all()

    if not Medicine.query.first():
        db.session.add(Medicine(name="Paracetamol", category="Fever", price=50, is_popular=True))
        db.session.add(Medicine(name="Aspirin", category="Pain", price=30, is_popular=True))
        db.session.add(Medicine(name="Cough Syrup", category="Cold", price=120, is_popular=True))
        db.session.add(Medicine(name="Vitamin C", category="Health", price=80, is_popular=True))
        db.session.add(Medicine(name="Dolo 650", category="Fever", price=60, is_popular=True))
        db.session.add(Medicine(name="Ibuprofen", category="Pain", price=40, is_popular=True))
        db.session.commit()

# -------------------
# RUN APP
# -------------------
if __name__ == '__main__':
    app.run(debug=True)
