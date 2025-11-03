from .utils import get_cart_items_count

def cart_context(request):
    return {
        'cart_items_count': get_cart_items_count(request)
    }

def categories_processor(request):
    from .models import Category
    return {
        'categories': Category.objects.filter(is_active=True)
    }