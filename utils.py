from flask import session

def get_cart():
    cart = session.get("cart")
    if not isinstance(cart, list):
        cart = []
        session["cart"] = cart
    return cart