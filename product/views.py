from django.shortcuts import render
from django.views.generic import ListView, DetailView, TemplateView
from django.db.models import Q
from .models import Category
from .models import Product
from django.http import JsonResponse
from django.views import View
from django.shortcuts import get_object_or_404
class IndexView(TemplateView):
    template_name = 'product/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(is_active=True)
        context['featured_products'] = Product.objects.filter(
            is_active=True,
            quantity__gt=0
        ).select_related('category')[:8]
        return context


class ProductListView(ListView):
    model = Product
    template_name = 'product/product_list.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        return Product.objects.filter(
            is_active=True,
            quantity__gt=0
        ).select_related('category').order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(is_active=True)
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = 'product/product_detail.html'
    context_object_name = 'product'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return Product.objects.filter(is_active=True).select_related('category')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(is_active=True)

        # Похожие товары из той же категории
        context['related_products'] = Product.objects.filter(
            category=self.object.category,
            is_active=True,
            quantity__gt=0
        ).exclude(id=self.object.id)[:4]

        return context


class CategoryListView(ListView):
    model = Category
    template_name = 'product/category_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        return Category.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем количество товаров для каждой категории
        for category in context['categories']:
            category.product_count = Product.objects.filter(
                category=category,
                is_active=True,
                quantity__gt=0
            ).count()
        return context


class CategoryDetailView(DetailView):
    model = Category
    template_name = 'product/category_detail.html'
    context_object_name = 'category'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return Category.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(is_active=True)
        context['products'] = Product.objects.filter(
            category=self.object,
            is_active=True,
            quantity__gt=0
        ).select_related('category')
        return context


class ProductSearchView(ListView):
    model = Product
    template_name = 'product/search_results.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        query = self.request.GET.get('q', '')
        if query:
            return Product.objects.filter(
                Q(name__icontains=query) |
                Q(short_description__icontains=query) |
                Q(full_description__icontains=query) |
                Q(category__name__icontains=query),
                is_active=True,
                quantity__gt=0
            ).select_related('category').distinct()
        return Product.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(is_active=True)
        context['query'] = self.request.GET.get('q', '')
        return context


def simple_add_to_cart(request, product_id):
    """Упрощенное добавление в корзину через сессии"""
    # Проверяем авторизацию
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'message': 'Для добавления товаров в корзину необходимо войти в систему',
            'login_required': True
        })

    if request.method == 'POST':
        try:
            product = get_object_or_404(Product, id=product_id, is_active=True, quantity__gt=0)

            if 'cart' not in request.session:
                request.session['cart'] = {}

            cart = request.session['cart']
            product_id_str = str(product_id)

            if product_id_str in cart:
                cart[product_id_str] += 1
            else:
                cart[product_id_str] = 1

            request.session.modified = True

            total_quantity = sum(cart.values())

            return JsonResponse({
                'success': True,
                'message': f'Товар "{product.name}" добавлен в корзину',
                'cart_items_count': total_quantity
            })

        except Product.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Товар не найден или недоступен'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Ошибка: {str(e)}'
            })

    return JsonResponse({'success': False, 'message': 'Неверный метод'})


class SimpleCartView(View):
    """Упрощенный просмотр корзины"""

    def get(self, request):
        cart_data = request.session.get('cart', {})
        cart_items = []
        total_price = 0
        total_quantity = 0

        # Получаем информацию о товарах из базы
        for product_id_str, quantity in cart_data.items():
            try:
                product = Product.objects.get(
                    id=int(product_id_str),
                    is_active=True
                )
                item_total = product.price * quantity

                cart_items.append({
                    'product': product,
                    'quantity': quantity,
                    'total_price': item_total
                })

                total_price += item_total
                total_quantity += quantity

            except (Product.DoesNotExist, ValueError):
                continue

        context = {
            'cart_items': cart_items,
            'total_price': total_price,
            'total_quantity': total_quantity,
            'cart_items_count': total_quantity,
            'categories': Category.objects.filter(is_active=True)
        }

        return render(request, 'product/cart.html', context)


def simple_remove_from_cart(request, product_id):
    """Удаление товара из корзины"""
    if request.method == 'POST':
        if 'cart' in request.session:
            cart = request.session['cart']
            product_id_str = str(product_id)

            if product_id_str in cart:
                try:
                    product = Product.objects.get(id=product_id)
                    product_name = product.name
                except Product.DoesNotExist:
                    product_name = "Товар"

                del cart[product_id_str]
                request.session.modified = True

                total_quantity = sum(cart.values())

                return JsonResponse({
                    'success': True,
                    'message': f'Товар "{product_name}" удален из корзины',
                    'cart_items_count': total_quantity
                })

    return JsonResponse({
        'success': False,
        'message': 'Товар не найден в корзине'
    })


def simple_update_cart_quantity(request, product_id):
    """Обновление количества товара в корзине"""
    if request.method == 'POST' and 'cart' in request.session:
        try:
            import json
            data = json.loads(request.body)
            quantity = int(data.get('quantity', 1))

            if quantity < 1:
                return JsonResponse({
                    'success': False,
                    'message': 'Количество должно быть больше 0'
                })

            cart = request.session['cart']
            product_id_str = str(product_id)

            if product_id_str in cart:
                cart[product_id_str] = quantity
                request.session.modified = True

                total_quantity = sum(cart.values())

                return JsonResponse({
                    'success': True,
                    'cart_items_count': total_quantity
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Товар не найден в корзине'
                })

        except (ValueError, json.JSONDecodeError) as e:
            return JsonResponse({
                'success': False,
                'message': f'Ошибка данных: {str(e)}'
            })

    return JsonResponse({
        'success': False,
        'message': 'Ошибка обновления'
    })