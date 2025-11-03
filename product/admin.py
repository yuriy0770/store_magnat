from django.contrib import admin
from django.utils.html import format_html
from decimal import Decimal
from product.models import Category, Product


@admin.register(Category)
class AdminCategory(admin.ModelAdmin):
    list_display = [
        'image_preview',
        'name',
        'product_count',
        'is_active',
        'created_at',
        'updated_at'
    ]
    list_display_links = ['name', 'image_preview']
    list_editable = ['is_active']
    search_fields = ['name', 'description', 'slug']
    list_filter = [
        'is_active',
        'created_at',
        'updated_at'
    ]
    readonly_fields = [
        'created_at',
        'updated_at',
        'image_preview_large',
        'product_count'
    ]
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'slug', 'description')
        }),
        ('Изображение', {
            'fields': ('image', 'image_preview_large')
        }),
        ('Статус и даты', {
            'fields': ('is_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    prepopulated_fields = {'slug': ('name',)}
    list_per_page = 20
    actions = ['activate_categories', 'deactivate_categories']
    date_hierarchy = 'created_at'

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 5px;" />',
                obj.image.url
            )
        return "—"

    image_preview.short_description = 'Изображение'

    def image_preview_large(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="200" height="200" style="object-fit: cover; border-radius: 10px;" />',
                obj.image.url
            )
        return "Изображение не загружено"

    image_preview_large.short_description = 'Предпросмотр'

    def product_count(self, obj):
        count = obj.products.count()
        return format_html(
            '<span style="color: {};">{}</span>',
            'green' if count > 0 else 'red',
            f'{count} товаров'
        )

    product_count.short_description = 'Кол-во товаров'

    def activate_categories(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'Активировано {updated} категорий')

    activate_categories.short_description = "Активировать выбранные категории"

    def deactivate_categories(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'Деактивировано {updated} категорий')

    deactivate_categories.short_description = "Деактивировать выбранные категории"


@admin.register(Product)
class AdminProduct(admin.ModelAdmin):
    list_display = [
        'image_preview',
        'name',
        'category',
        'price_display',
        'quantity_display',
        'is_active',
        'created_at'
    ]
    list_display_links = ['name', 'image_preview']
    list_editable = ['is_active']
    list_filter = [
        'category',
        'is_active',
        'created_at',
        'updated_at',
    ]
    search_fields = [
        'name',
        'sku',
        'short_description',
        'full_description',
        'category__name'
    ]
    readonly_fields = [
        'created_at',
        'updated_at',
        'image_preview_large',
        'profit_margin'
    ]
    fieldsets = (
        ('Основная информация', {
            'fields': (
                'category',
                'name',
                'sku',
                'slug'
            )
        }),
        ('Описания', {
            'fields': (
                'short_description',
                'full_description'
            ),
            'classes': ('collapse',)
        }),
        ('Цена и количество', {
            'fields': (
                'price',
                'quantity',
            )
        }),
        ('Изображения', {
            'fields': (
                'image',
                'image_url',
                'image_preview_large'
            )
        }),
        ('Статус и даты', {
            'fields': (
                'is_active',
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )
    prepopulated_fields = {'slug': ('name',)}
    autocomplete_fields = ['category']
    list_per_page = 25
    date_hierarchy = 'created_at'
    actions = [
        'activate_products',
        'deactivate_products',
    ]
    save_on_top = True

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 5px;" />',
                obj.image.url
            )
        elif obj.image_url:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 5px;" />',
                obj.image_url
            )
        return "—"

    image_preview.short_description = 'Фото'

    def image_preview_large(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="300" height="300" style="object-fit: cover; border-radius: 10px;" />',
                obj.image.url
            )
        elif obj.image_url:
            return format_html(
                '<img src="{}" width="300" height="300" style="object-fit: cover; border-radius: 10px;" />',
                obj.image_url
            )
        return "Изображение не загружено"

    image_preview_large.short_description = 'Предпросмотр'

    def price_display(self, obj):
        if obj.price:
            return format_html(
                '<span style="color: green; font-weight: bold;">{} ₽</span>',
                obj.price
            )
        return "—"

    price_display.short_description = 'Цена'

    def quantity_display(self, obj):
        color = 'green'
        if obj.quantity == 0:
            color = 'red'
        elif obj.quantity < 10:
            color = 'orange'

        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.quantity
        )

    quantity_display.short_description = 'Остаток'

    def profit_margin(self, obj):
        """
        Исправленный метод расчета маржи
        """
        if obj.price and obj.price > 0:
            # Используем Decimal для расчетов
            cost_price = obj.price * Decimal('0.6')  # себестоимость 60%
            margin = ((obj.price - cost_price) / obj.price) * 100

            color = 'green' if margin > 30 else 'orange' if margin > 15 else 'red'
            return format_html(
                '<span style="color: {}; font-weight: bold;">{:.1f}%</span>',
                color,
                float(margin)  # конвертируем в float для форматирования
            )
        return "—"

    profit_margin.short_description = 'Маржа'

    def activate_products(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'Активировано {updated} товаров')

    activate_products.short_description = "Активировать выбранные товары"

    def deactivate_products(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'Деактивировано {updated} товаров')

    deactivate_products.short_description = "Деактивировать выбранные товары"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category')
