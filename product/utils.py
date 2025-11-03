def get_cart_items_count(request):
    if 'cart' in request.session:
        cart = request.session['cart']
        return sum(cart.values())
    return 0

def get_or_create_cart(request):
    return None