from django.core.management.base import BaseCommand
from inventory.models import Product


# Stock levels are set at the 5-store total scale to match Prophet forecast scale.
# Prophet models predict weekly demand across all 5 stores (~4700-4870 units/week).
# current_stock = avg_single_store_stock * 5 * weeks_of_buffer
# reorder_point = 1 week of total demand (triggers reorder alert when < 7 days stock left)
#
# Deliberate spread of stock health for a realistic demo:
#   CRITICAL  (< 7 days)  : P0001, P0003, P0006, P0008, P0016, P0018
#   WARNING   (7-14 days) : P0002, P0005, P0009, P0012, P0017, P0019
#   OK        (> 14 days) : P0004, P0007, P0010, P0011, P0013, P0014, P0015, P0020

PRODUCTS = [
    # --- CRITICAL (3-6 days of stock) ---
    {'product_id': 'P0001', 'name': 'Organic Whole Milk (1L)',        'category': 'food',        'price':  54.55, 'current_stock':   850, 'reorder_point': 4769},
    {'product_id': 'P0003', 'name': 'Basmati Rice (5kg)',             'category': 'food',        'price':  54.89, 'current_stock':   950, 'reorder_point': 4724},
    {'product_id': 'P0006', 'name': 'Breakfast Cereal (500g)',        'category': 'food',        'price':  54.77, 'current_stock':   780, 'reorder_point': 4760},
    {'product_id': 'P0008', 'name': 'USB-C Fast Charger (65W)',       'category': 'electronics', 'price':  55.35, 'current_stock':   900, 'reorder_point': 4678},
    {'product_id': 'P0016', 'name': 'Multigrain Bread (600g)',        'category': 'food',        'price':  54.83, 'current_stock':   700, 'reorder_point': 4869},
    {'product_id': 'P0018', 'name': 'Noise Cancelling Earbuds',       'category': 'electronics', 'price':  54.82, 'current_stock':   650, 'reorder_point': 4717},

    # --- WARNING (8-13 days of stock) ---
    {'product_id': 'P0002', 'name': 'Ergonomic Office Chair',         'category': 'home',        'price':  55.27, 'current_stock':  1500, 'reorder_point': 4671},
    {'product_id': 'P0005', 'name': 'Instant Noodles Pack (12x)',     'category': 'food',        'price':  55.02, 'current_stock':  1100, 'reorder_point': 4823},
    {'product_id': 'P0009', 'name': 'Wooden Bookshelf (5-Tier)',      'category': 'home',        'price':  55.16, 'current_stock':  1800, 'reorder_point': 4808},
    {'product_id': 'P0012', 'name': "Men's Running Jacket",           'category': 'clothing',    'price':  54.96, 'current_stock':  2400, 'reorder_point': 4708},
    {'product_id': 'P0017', 'name': "Women's Casual Dress",           'category': 'clothing',    'price':  54.65, 'current_stock':  1650, 'reorder_point': 4793},
    {'product_id': 'P0019', 'name': 'Slim Fit Chino Trousers',        'category': 'clothing',    'price':  55.08, 'current_stock':  1400, 'reorder_point': 4768},

    # --- OK (15-30+ days of stock) ---
    {'product_id': 'P0004', 'name': 'Smart LED Television 43"',       'category': 'electronics', 'price':  55.54, 'current_stock': 12000, 'reorder_point': 4745},
    {'product_id': 'P0007', 'name': 'Wireless Bluetooth Headphones',  'category': 'electronics', 'price':  54.92, 'current_stock': 15000, 'reorder_point': 4781},
    {'product_id': 'P0010', 'name': 'LEGO Classic Building Set',      'category': 'other',       'price':  55.36, 'current_stock': 18000, 'reorder_point': 4754},
    {'product_id': 'P0011', 'name': 'Laptop 15" (Intel i5)',          'category': 'electronics', 'price':  56.43, 'current_stock': 10500, 'reorder_point': 4782},
    {'product_id': 'P0013', 'name': 'Extra Virgin Olive Oil (750ml)', 'category': 'food',        'price':  55.06, 'current_stock': 22000, 'reorder_point': 4794},
    {'product_id': 'P0014', 'name': 'Remote Control Racing Car',      'category': 'other',       'price':  55.76, 'current_stock': 14000, 'reorder_point': 4861},
    {'product_id': 'P0015', 'name': 'Sectional Sofa (3-Seater)',      'category': 'home',        'price':  54.77, 'current_stock': 19500, 'reorder_point': 4858},
    {'product_id': 'P0020', 'name': 'Toy Kitchen Playset',            'category': 'other',       'price':  55.52, 'current_stock': 11000, 'reorder_point': 4862},
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
