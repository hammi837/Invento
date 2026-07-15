import joblib
import pandas as pd
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from inventory.models import ProductForecast
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'Generate weekly demand forecasts for all products using trained Prophet models'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days-ahead',
            type=int,
            default=7,
            help='How many days ahead to forecast (default: 7)',
        )

    def handle(self, *args, **kwargs):
        days_ahead = kwargs['days_ahead']
        models_dir = Path(settings.BASE_DIR) / 'inventory' / 'ml_models'
        model_files = list(models_dir.glob('*_model.pkl'))

        if not model_files:
            self.stdout.write(self.style.ERROR(
                f"No model files found in {models_dir}\n"
                f"Copy your .pkl files there and try again."
            ))
            return

        forecast_date = datetime.today() + timedelta(days=days_ahead)
        self.stdout.write(f"Generating forecasts for {forecast_date.date()} ({len(model_files)} models found)\n")

        success_count = 0
        failed = []

        for model_path in sorted(model_files):
            product_id = model_path.stem.replace('_model', '')

            try:
                model = joblib.load(model_path)

                future = pd.DataFrame({
                    'ds': [forecast_date],
                    'Holiday/Promotion': [0],
                })
                forecast = model.predict(future)
                predicted = max(0.0, float(forecast['yhat'].values[0]))

                ProductForecast.objects.update_or_create(
                    product_id=product_id,
                    forecast_date=forecast_date.date(),
                    defaults={'predicted_units': predicted},
                )
                self.stdout.write(f"  {product_id}: {predicted:.1f} units")
                success_count += 1

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  {product_id}: FAILED — {e}"))
                failed.append(product_id)

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(
            f"Done. {success_count}/{len(model_files)} forecasts generated."
        ))
        if failed:
            self.stdout.write(self.style.WARNING(
                f"Failed products: {', '.join(failed)}"
            ))
