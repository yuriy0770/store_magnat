import uuid
from django.contrib.auth.models import User
from django.db import models
from django.core.validators import MinValueValidator


class Category(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название')
    slug = models.SlugField(max_length=50, unique=True, verbose_name='Слаг')
    description = models.TextField(blank=True, verbose_name='Описание')
    image = models.ImageField(upload_to='category/', verbose_name='Изображение')
    is_active = models.BooleanField(default=True, verbose_name='Активна')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категория', related_name='products')
    name = models.CharField(max_length=100, verbose_name='Название')
    sku = models.CharField(max_length=50, unique=True, verbose_name='Артикул (SKU)', blank=True)
    slug = models.SlugField(max_length=100, unique=True, verbose_name='Слаг')
    short_description = models.TextField(max_length=200, blank=True, verbose_name='Краткое описание')
    full_description = models.TextField(blank=True, verbose_name='Полное описание')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена', validators=[MinValueValidator(0)])
    quantity = models.PositiveIntegerField(default=0, verbose_name='Количество на складе')
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name='Изображение товара')
    image_url = models.URLField(blank=True, verbose_name='URL изображения')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    def save(self, *args, **kwargs):
        if not self.sku:
            self.sku = f"SKU-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        ordering = ['name']  # добавлено: сортировка по названию


from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal

class Cart(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Используем кастомную модель пользователя
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Пользователь'
    )
    session_key = models.CharField(
        max_length=40,
        null=True,
        blank=True,
        verbose_name='Ключ сессии'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )

    def __str__(self):
        if self.user:
            return f"Корзина пользователя {self.user.username}"
        return f"Корзина (аноним) {self.session_key}"

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())

    @property
    def total_quantity(self):
        return sum(item.quantity for item in self.items.all())

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'

class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Корзина'
    )
    product = models.ForeignKey(
        'Product',
        on_delete=models.CASCADE,
        verbose_name='Товар'
    )
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name='Количество'
    )
    added_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добавления'
    )

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    @property
    def total_price(self):
        return self.product.price * self.quantity

    class Meta:
        verbose_name = 'Элемент корзины'
        verbose_name_plural = 'Элементы корзины'
        unique_together = ['cart', 'product']
