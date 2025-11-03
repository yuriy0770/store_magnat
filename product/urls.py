from django.urls import path
from . import views

app_name = 'product'


urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('products/<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/<slug:slug>/', views.CategoryDetailView.as_view(), name='category_detail'),
    path('search/', views.ProductSearchView.as_view(), name='product_search'),
    path('cart/add/<int:product_id>/', views.simple_add_to_cart, name='add_to_cart'),
    path('cart/', views.SimpleCartView.as_view(), name='cart'),
    path('cart/remove/<int:product_id>/', views.simple_remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:product_id>/', views.simple_update_cart_quantity, name='update_cart_quantity'),
]