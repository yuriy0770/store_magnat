def get_cart_items_count(request):
    """
    Возвращает количество товаров в корзине из сессии
    """
    if 'cart' in request.session:
        cart = request.session['cart']
        return sum(cart.values())
    return 0

# Если ранее использовались модели корзины, оставь эту функцию для совместимости
def get_or_create_cart(request):
    """
    Функция для совместимости (если где-то еще используется)
    """
    return None