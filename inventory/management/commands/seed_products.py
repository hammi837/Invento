from django.core.management.base import BaseCommand
from inventory.models import Product


# Seed data for the 20 products from the Kaggle retail dataset.
# Update names, categories, prices and stock levels to match your actual dataset.
PRODUCTS = [
    {'product_id': 'P0001', 'name': 'Product 0001', 'category': 'electronics',  'price': 199.99, 'current_stock': 1500, 'reorder_point': 300},
    {'product_id': 'P0002', 'name': 'Product 0002', 'category': 'clothing',     'price':  49.99, 'current_stock':  800, 'reorder_point': 150},
    {'product_id': 'P0003', 'name': 'Product 0003', 'category': 'food',         'price':  12.99, 'current_stock': 2000, 'reorder_point': 500},
    {'product_id': 'P0004', 'name': 'Product 0004', 'category': 'home',         'price':  89.99, 'current_stock':  600, 'reorder_point': 100},
    {'product_id': 'P0005', 'name': 'Product 0005', 'category': 'sports',       'price':  34.99, 'current_stock':  900, 'reorder_point': 200},
    {'product_id': 'P0006', 'name': 'Product 0006', 'category': 'electronics',  'price': 299.99, 'current_stock':  400, 'reorder_point': 100},
    {'product_id': 'P0007', 'name': 'Product 0007', 'category': 'clothing',     'price':  24.99, 'current_stock':  300, 'reorder_point':  50},
    {'product_id': 'P0008', 'name': 'Product 0008', 'category': 'food',         'price':   8.99, 'current_stock': 3000, 'reorder_point': 600},
    {'product_id': 'P0009', 'name': 'Product 0009', 'category': 'home',         'price':  59.99, 'current_stock': 1200, 'reorder_point': 200},
    {'product_id': 'P0010', 'name': 'Product 0010', 'category': 'sports',       'price':  74.99, 'current_stock':  500, 'reorder_point': 100},
    {'product_id': 'P0011', 'name': 'Product 0011', 'category': 'electronics',  'price': 149.99, 'current_stock': 2500, 'reorder_point': 400},
    {'product_id': 'P0012', 'name': 'Product 0012', 'category': 'clothing',     'price':  39.99, 'current_stock': 1800, 'reorder_point': 300},
    {'product_id': 'P0013', 'name': 'Product 0013', 'category': 'food',         'price':  15.99, 'current_stock':  700, 'reorder_point': 200},
    {'product_id': 'P0014', 'name': 'Product 0014', 'category': 'home',         'price': 129.99, 'current_stock':  350, 'reorder_point':  75},
    {'product_id': 'P0015', 'name': 'Product 0015', 'category': 'sports',       'price':  54.99, 'current_stock': 1100, 'reorder_point': 200},
    {'product_id': 'P0016', 'name': 'Product 0016', 'category': 'electronics',  'price': 399.99, 'current_stock':  250, 'reorder_point':  50},
    {'product_id': 'P0017', 'name': 'Product 0017', 'category': 'clothing',     'price':  69.99, 'current_stock':  900, 'reorder_point': 150},
    {'product_id': 'P0018', 'name': 'Product 0018', 'category': 'food',         'price':  19.99, 'current_stock': 1600, 'reorder_point': 400},
    {'product_id': 'P0019', 'name': 'Product 0019', 'category': 'home',         'price':  44.99, 'current_stock':  750, 'reorder_point': 150},
    {'product_id': 'P0020', 'name': 'Product 0020', 'category': 'sports',       'price':  94.99, 'current_stock':  420, 'reorder_point': 100},
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
