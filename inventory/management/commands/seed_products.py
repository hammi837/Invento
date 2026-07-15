from django.core.management.base import BaseCommand
from inventory.models import Product


# Seed data for the 20 products from the Kaggle retail dataset.
# Update names, categories, prices and stock levels to match your actual dataset.
# Data sourced from retail_store_inventory.csv (Kaggle).
# Category = most frequent category per product across all stores.
# Price = average price from dataset (rounded to 2dp).
# current_stock = realistic starting stock based on avg inventory level in dataset.
# reorder_point = ~30% of avg stock level (standard retail rule of thumb).
PRODUCTS = [
    {'product_id': 'P0001', 'name': 'Organic Whole Milk (1L)',        'category': 'food',          'price':  54.55, 'current_stock': 273, 'reorder_point':  80},
    {'product_id': 'P0002', 'name': 'Ergonomic Office Chair',         'category': 'home',          'price':  55.27, 'current_stock': 271, 'reorder_point':  80},
    {'product_id': 'P0003', 'name': 'Basmati Rice (5kg)',             'category': 'food',          'price':  54.89, 'current_stock': 275, 'reorder_point':  80},
    {'product_id': 'P0004', 'name': 'Smart LED Television 43"',       'category': 'electronics',   'price':  55.54, 'current_stock': 272, 'reorder_point':  80},
    {'product_id': 'P0005', 'name': 'Instant Noodles Pack (12x)',     'category': 'food',          'price':  55.02, 'current_stock': 273, 'reorder_point':  80},
    {'product_id': 'P0006', 'name': 'Breakfast Cereal (500g)',        'category': 'food',          'price':  54.77, 'current_stock': 274, 'reorder_point':  80},
    {'product_id': 'P0007', 'name': 'Wireless Bluetooth Headphones',  'category': 'electronics',   'price':  54.92, 'current_stock': 275, 'reorder_point':  80},
    {'product_id': 'P0008', 'name': 'USB-C Fast Charger (65W)',       'category': 'electronics',   'price':  55.35, 'current_stock': 273, 'reorder_point':  80},
    {'product_id': 'P0009', 'name': 'Wooden Bookshelf (5-Tier)',      'category': 'home',          'price':  55.16, 'current_stock': 275, 'reorder_point':  80},
    {'product_id': 'P0010', 'name': 'LEGO Classic Building Set',      'category': 'other',         'price':  55.36, 'current_stock': 275, 'reorder_point':  80},
    {'product_id': 'P0011', 'name': 'Laptop 15" (Intel i5)',          'category': 'electronics',   'price':  56.43, 'current_stock': 273, 'reorder_point':  80},
    {'product_id': 'P0012', 'name': "Men's Running Jacket",           'category': 'clothing',      'price':  54.96, 'current_stock': 273, 'reorder_point':  80},
    {'product_id': 'P0013', 'name': 'Extra Virgin Olive Oil (750ml)', 'category': 'food',          'price':  55.06, 'current_stock': 275, 'reorder_point':  80},
    {'product_id': 'P0014', 'name': 'Remote Control Racing Car',      'category': 'other',         'price':  55.76, 'current_stock': 278, 'reorder_point':  83},
    {'product_id': 'P0015', 'name': 'Sectional Sofa (3-Seater)',      'category': 'home',          'price':  54.77, 'current_stock': 276, 'reorder_point':  82},
    {'product_id': 'P0016', 'name': 'Multigrain Bread (600g)',        'category': 'food',          'price':  54.83, 'current_stock': 278, 'reorder_point':  83},
    {'product_id': 'P0017', 'name': "Women's Casual Dress",           'category': 'clothing',      'price':  54.65, 'current_stock': 278, 'reorder_point':  83},
    {'product_id': 'P0018', 'name': 'Noise Cancelling Earbuds',       'category': 'electronics',   'price':  54.82, 'current_stock': 273, 'reorder_point':  80},
    {'product_id': 'P0019', 'name': 'Slim Fit Chino Trousers',        'category': 'clothing',      'price':  55.08, 'current_stock': 275, 'reorder_point':  80},
    {'product_id': 'P0020', 'name': 'Toy Kitchen Playset',            'category': 'other',         'price':  55.52, 'current_stock': 277, 'reorder_point':  83},
]


class Command(BaseCommand):
    help = 'Seed the Product table with the 20 products from the retail dataset'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Delete all existing products before seeding',
        )

    def handle(self, *args, **kwargs):
        if kwargs['reset']:
            count, _ = Product.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"Deleted {count} existing products."))

        created_count = 0
        updated_count = 0

        for data in PRODUCTS:
            _, created = Product.objects.update_or_create(
                product_id=data['product_id'],
                defaults=data,
            )
            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Done. {created_count} created, {updated_count} updated."
        ))
