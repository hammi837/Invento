# Invento — AI-Powered Inventory Management System

![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python)
![Django](https://img.shields.io/badge/Django-5.2-092E20?logo=django)
![DRF](https://img.shields.io/badge/DRF-3.17-red?logo=django)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql)
![Prophet](https://img.shields.io/badge/Prophet-1.3-blue)
![License](https://img.shields.io/badge/license-MIT-green)

AI-powered inventory management system with weekly demand forecasting. Django + PostgreSQL backend with 20 trained Facebook Prophet time-series models predicting weekly product demand (avg. 14.35% MAPE).

---

## Features

- **Demand Forecasting** — 20 per-product Prophet models predicting weekly units sold
- **REST API** — DRF endpoints consumed by the React frontend
- **Stock Alert Logic** — days-until-stockout calculation per product
- **Django Admin** — full CRUD visibility into forecast data
- **Production-Ready** — split settings (dev/prod), WhiteNoise, Sentry, HTTPS headers
- **Management Command** — `generate_forecasts` regenerates all 20 forecasts in one command

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django 5.2, Django REST Framework |
| Database | PostgreSQL |
| ML / Forecasting | Facebook Prophet, pandas, joblib |
| Frontend | React (separate repo) |
| Auth | Django session + token auth |
| Deployment | Gunicorn + Nginx (AWS) |

---

## Project Structure

```
inventory-system/
├── core/
│   ├── settings/
│   │   ├── base.py          # shared config
│   │   ├── development.py   # debug toolbar, relaxed CORS
│   │   └── production.py    # HTTPS, WhiteNoise, Sentry
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── inventory/
│   ├── management/commands/
│   │   └── generate_forecasts.py   # runs all 20 Prophet models
│   ├── migrations/
│   ├── ml_models/           # .pkl files go here (not in git)
│   ├── models.py            # ProductForecast model
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── requirements/
│   ├── base.txt
│   ├── development.txt
│   └── production.txt
├── logs/
├── .env.example
└── manage.py
```

---

## Local Setup

### Prerequisites
- Python 3.10+
- PostgreSQL 14+
- Git

### 1. Clone and create virtual environment

```bash
git clone https://github.com/hammi837/Invento.git
cd Invento
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements/development.txt
```

### 3. Configure environment

```bash
copy .env.example .env   # Windows
cp .env.example .env     # Mac/Linux
```

Edit `.env` with your PostgreSQL credentials:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=inventory
DB_USER=postgres
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=5432

CORS_ALLOWED_ORIGINS=http://localhost:3000
```

### 4. Create the database

```bash
createdb inventory
```

### 5. Run migrations and create superuser

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 6. Add ML models and generate forecasts

Place your trained `.pkl` files in `inventory/ml_models/` then:

```bash
python manage.py generate_forecasts
# or forecast 14 days ahead:
python manage.py generate_forecasts --days-ahead 14
```

### 7. Start the dev server

```bash
python manage.py runserver
```

- API: http://127.0.0.1:8000/api/forecasts/
- Admin: http://127.0.0.1:8000/admin/

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/forecasts/` | All forecasts (paginated) |
| GET | `/api/forecasts/?product_id=P0001` | Filter by product |
| GET | `/api/forecasts/?ordering=forecast_date` | Sort by date |
| GET | `/api/forecasts/<id>/` | Single forecast record |

### Example response

```json
{
  "count": 20,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "product_id": "P0001",
      "forecast_date": "2026-07-22",
      "predicted_units": 612.3,
      "current_stock": null,
      "days_until_stockout": null,
      "generated_at": "2026-07-15T14:00:00Z"
    }
  ]
}
```

---

## ML Models

The trained Prophet forecasting models (`.pkl` files) are **not included** in this repository, following standard ML engineering practice — model artifacts are regenerable outputs of the training code, not source code themselves.

### To regenerate the models

1. Open `notebooks/train_models.ipynb` in Google Colab or Jupyter
2. Upload the dataset: `retail_store_inventory.csv`
   ([source dataset](https://www.kaggle.com/datasets/anirudhchauhan/retail-store-inventory-forecasting-dataset))
3. Run all cells — trains 20 Prophet models (one per product) and saves them as `.pkl` files
4. Download the generated models and place them in `inventory/ml_models/`

### Model performance

**Average MAPE of 14.35%** across 20 products on held-out test data (weekly demand forecasting).

| Metric | Value |
|---|---|
| Avg MAPE | 14.35% |
| Best product | P0014 (8.42% MAPE) |
| Worst product | P0008 (20.77% MAPE) |
| Forecast granularity | Weekly |
| Model type | Facebook Prophet (per-product) |

---

## Running in Production

```bash
# Install production dependencies
pip install -r requirements/production.txt

# Set environment variable
set DJANGO_SETTINGS_MODULE=core.settings.production   # Windows
export DJANGO_SETTINGS_MODULE=core.settings.production # Mac/Linux

# Collect static files
python manage.py collectstatic --noinput

# Start Gunicorn
gunicorn core.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

---

## License

MIT
