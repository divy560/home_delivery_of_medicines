from flask import Blueprint, session, redirect, url_for, render_template
from models import Medicine
from utils import get_cart

cart_bp = Blueprint('cart', __name__)


# ---------------------------
# VIEW CART INIT SAFETY
# ---------------------------
def ensure_cart():
    if "cart" not in session:
        session["cart"] = []


# ---------------------------
# ADD TO CART
# ---------------------------
@cart_bp.route('/add_to_cart/<int:id>')
def add_to_cart(id):
    ensure_cart()
    cart = get_cart()

    for item in cart:
        if item["id"] == id:
            item["quantity"] += 1
            break
    else:
        cart.append({
            "id": id,
            "quantity": 1
        })

    session["cart"] = cart
    session.modified = True

    return redirect(url_for('cart.view_cart'))


# ---------------------------
# VIEW CART
# ---------------------------
@cart_bp.route('/cart')
def view_cart():
    ensure_cart()
    cart = get_cart()

    cart_items = []
    total_price = 0

    for item in cart:
        med = Medicine.query.get(item["id"])

        if not med:
            continue

        total = med.price * item["quantity"]

        cart_items.append({
            "id": med.id,
            "name": med.name,
            "price": med.price,
            "quantity": item["quantity"],
            "total": total
        })

        total_price += total

    return render_template("cart.html",
                           cart=cart_items,
                           total_price=total_price)


# ---------------------------
# INCREASE QUANTITY
# ---------------------------
@cart_bp.route('/increase/<int:id>')
def increase(id):
    ensure_cart()
    cart = get_cart()

    for item in cart:
        if item["id"] == id:
            item["quantity"] += 1
            break

    session["cart"] = cart
    return redirect(url_for('cart.view_cart'))


# ---------------------------
# DECREASE QUANTITY
# ---------------------------
@cart_bp.route('/decrease/<int:id>')
def decrease(id):
    ensure_cart()
    cart = get_cart()

    for item in cart:
        if item["id"] == id:
            if item["quantity"] > 1:
                item["quantity"] -= 1
            break

    session["cart"] = cart
    return redirect(url_for('cart.view_cart'))


# ---------------------------
# REMOVE ITEM
# ---------------------------
@cart_bp.route('/remove/<int:id>')
def remove(id):
    ensure_cart()
    cart = get_cart()

    session["cart"] = [item for item in cart if item["id"] != id]

    return redirect(url_for('cart.view_cart'))