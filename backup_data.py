import os
import django
import json
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from product.models import Category, Product


def backup_data():
    backup = {
        'timestamp': datetime.now().isoformat(),
        'categories': [],
        'products': []
    }

    # Бэкап категорий
    for category in Category.objects.all():
        backup['categories'].append({
            'id': category.id,
            'name': category.name,
            'slug': category.slug,
            'description': category.description,
            'is_active': category.is_active
        })

    # Бэкап товаров
    for product in Product.objects.all():
        backup['products'].append({
            'id': product.id,
            'name': product.name,
            'slug': product.slug,
            'sku': product.sku,
            'category_id': product.category_id,
            'short_description': product.short_description,
            'full_description': product.full_description,
            'price': str(product.price),
            'quantity': product.quantity,
            'is_active': product.is_active
        })

    # Сохраняем в файл
    with open('backup_data.json', 'w', encoding='utf-8') as f:
        json.dump(backup, f, ensure_ascii=False, indent=2)

    print(f"Backup created: {len(backup['categories'])} categories, {len(backup['products'])} products")


if __name__ == '__main__':
    backup_data()