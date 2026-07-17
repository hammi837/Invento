# Invento — Backend API

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Django-5.2-092E20?style=for-the-badge&logo=django&logoColor=white" />
  <img src="https://img.shields.io/badge/DRF-3.17-FF1709?style=for-the-badge&logo=django&logoColor=white" />
  <img src="https://img.shields.io/badge/PostgreSQL-16-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" />
  <img src="https://img.shields.io/badge/Prophet-1.3-0066CC?style=for-the-badge" />
  <img src="https://img.shields.io/badge/JWT-Auth-black?style=for-the-badge&logo=jsonwebtokens" />
  <img src="https://img.shields.io/badge/License-MIT-22c55e?style=for-the-badge" />
</p>

<p align="center">
  <strong>Django REST API powering an AI-driven inventory management system.</strong><br/>
  Role-based access control · Facebook Prophet demand forecasting · Full audit trail · JWT authentication
</p>

---

## What This Is

Invento's backend is a production-grade Django REST Framework API that sits between a React frontend and a machine learning layer. It handles:

- **Authentication** — JWT-based login with role claims embedded in tokens (Admin / Manager / Staff)
- **Authorization** — Custom DRF permission classes enforce role rules server-side on every endpoint
- **Demand Forecasting** — 20 trained Facebook Prophet models predict weekly product demand; forecasts are pre-computed and stored in PostgreSQL (not generated per request)
- **Audit Logging** — Every create/update/delete is recorded with user, timestamp, and details — immutable and visible to Manager+ roles
- **User Management** — Admin-only CRUD on users with self-lockout protection (can't delete/demote your own account)

---

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Web framework | Django 5.2 | Core application, ORM, admin |
| API | Django REST Framework 3.17 | REST endpoints, serializers, viewsets |
| Auth | djangorestframework-simplejwt 5.4 | JWT access + refresh tokens |
| Database | PostgreSQL 16 | Primary data store |
| ML / Forecasting | Facebook Prophet 1.3 | Per-product time-series demand forecasting |
| Data processing | pandas, joblib | Model serving and data preparation |
| Filtering | django-filter 24.3 | Query param filtering on list endpoints |
| Config | python-decouple | Environment-based secrets management |
| Production server | Gunicorn + Nginx | WSGI serving |
| Static files | WhiteNoise | Production static file serving |
| Error tracking | Sentry (production) | Exception monitoring |

---

## Project Structure

```
inventory-system/
├── core/
│   ├── settings/
│   │   ├── base.py           # Shared config: DB, DRF, CORS, logging, JWT
│   │   ├── development.py    # Debug toolbar, relaxed CORS, SQLite fallback
│   │   └── production.py     # HTTPS enforcement, WhiteNoise, Sentry
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── inventory/
│   ├── models.py             # User, Product, ProductForecast, AuditLog
│   ├── serializers.py        # Product + Forecast serializers with validation
│   ├── auth_serializers.py   # JWT + User CRUD serializers
│   ├── permissions.py        # IsAdmin, IsManagerOrAdmin, ReadOnlyOrManagerAbove
│   ├── views.py              # ViewSets and API views
│   ├── urls.py               # App-level URL routing
│   ├── admin.py              # Django admin (immutable AuditLog)
│   ├── management/
│   │   └── commands/
│   │       ├── generate_forecasts.py   # Load .pkl → predict → write to DB
│   │       └── seed_products.py        # Seed 20 products from dataset
│   └── ml_models/            # Trained Prophet .pkl files (git-ignored)
├── requirements/
│   ├── base.txt              # Shared dependencies
│   ├── development.txt       # + debug toolbar
│   └── production.txt        # + whitenoise, sentry
├── logs/
├── .env.example
└── manage.py
```

---

## Data Models

### User *(extends AbstractUser)*
Custom user model with `role` (admin/manager/staff), `phone`, and `is_active_employee`. Defined before the first migration — Django cannot swap the User model after migrations run.

### Product
Business-facing product record: `product_id` (e.g. P0001), `name`, `category`, `price`, `current_stock`, `reorder_point`.

### ProductForecast
ML output table — one row per product per forecast date. Holds `predicted_units`, `current_stock` snapshot, `days_until_stockout`, and a derived `stock_status` (critical / warning / ok). The API reads from here; forecasts are pre-computed on a schedule.

### AuditLog
Immutable action log: `user`, `action` (create/update/delete), `model_name`, `object_id`, `details`, `timestamp`. Written on every mutating action across Products and Users.

---

## Role-Based Access Control

| Endpoint | Staff | Manager | Admin |
|---|---|---|---|
| `GET /api/products/` | ✅ | ✅ | ✅ |
| `POST /api/products/` | ❌ | ✅ | ✅ |
| `PATCH /api/products/{id}/` | ❌ | ✅ | ✅ |
| `DELETE /api/products/{id}/` | ❌ | ❌ | ✅ |
| `GET /api/forecasts/` | ✅ | ✅ | ✅ |
| `GET /api/audit-logs/` | ❌ | ✅ | ✅ |
| `GET /api/users/` | ❌ | ❌ | ✅ |
| `POST /api/users/` | ❌ | ❌ | ✅ |
| `POST /api/users/{id}/deactivate/` | ❌ | ❌ | ✅ |

Permission is enforced **server-side** on every request — UI hiding is a UX convenience, not a security boundary.

---

## API Endpoints

| Method | Endpoint | Access | Description |
|---|---|---|---|
| `POST` | `/api/auth/login/` | Public | Obtain JWT tokens + role |
| `POST` | `/api/auth/refresh/` | Public | Refresh access token |
| `GET` | `/api/auth/me/` | Any role | Current user profile |
| `GET` | `/api/products/` | Staff+ | List products (filter, search, order) |
| `POST` | `/api/products/` | Manager+ | Create product |
| `PATCH` | `/api/products/{id}/` | Manager+ | Update product |
| `DELETE` | `/api/products/{id}/` | Admin | Delete product |
| `GET` | `/api/forecasts/` | Staff+ | Demand forecasts with stock status |
| `GET` | `/api/audit-logs/` | Manager+ | Immutable action history |
| `GET` | `/api/users/` | Admin | List users |
| `POST` | `/api/users/` | Admin | Create user |
| `PATCH` | `/api/users/{id}/` | Admin | Update user / reset password |
| `POST` | `/api/users/{id}/deactivate/` | Admin | Soft-disable login |
| `POST` | `/api/users/{id}/reactivate/` | Admin | Re-enable login |

All list endpoints support `?search=`, `?ordering=`, and `django-filter` query params.

---

## Local Setup

### Prerequisites
- Python 3.10+
- PostgreSQL 14+

### 1. Clone and activate virtual environment

```bash
git clone https://github.com/hammi837/Invento.git
cd Invento

python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
```

### 2. Install dependencies

```bash
pip install -r requirements/development.txt
```

### 3. Configure environment

```bash
copy .env.example .env    # Windows
cp .env.example .env      # Mac/Linux
```

Fill in `.env`:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=inventory
DB_USER=postgres
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=5432

CORS_ALLOWED_ORIGINS=http://localhost:5173
```

### 4. Create database and run migrations

```bash
createdb inventory
python manage.py migrate
```

### 5. Seed demo data

```bash
# Create default users (admin / manager / staff)
python manage.py seed_products

# Place .pkl model files in inventory/ml_models/, then:
python manage.py generate_forecasts
```

### 6. Create superuser and start server

```bash
python manage.py createsuperuser
python manage.py runserver
```

| URL | Purpose |
|---|---|
| `http://127.0.0.1:8000/api/` | REST API root |
| `http://127.0.0.1:8000/admin/` | Django admin |

---

## ML Models

Trained `.pkl` files are **not committed to Git** — model artifacts are regenerable build outputs, not source code. Committing them would bloat repository history permanently.

### Regenerating models

1. Open `notebooks/train_models.ipynb` in Google Colab or Jupyter
2. Upload `retail_store_inventory.csv` — [Kaggle dataset](https://www.kaggle.com/datasets/anirudhchauhan/retail-store-inventory-forecasting-dataset)
3. Run all cells — trains one Prophet model per product, saves as `.pkl`
4. Copy generated files into `inventory/ml_models/`
5. Run `python manage.py generate_forecasts`

### Model performance

| Metric | Value |
|---|---|
| Average MAPE | **14.35%** |
| Best product | P0014 — 8.42% MAPE |
| Worst product | P0008 — 20.77% MAPE |
| Granularity | Weekly demand |
| Architecture | One independent Prophet model per product |

Weekly granularity was chosen after testing daily (MAPE ~36%) — weekly aggregation reduces noise and matches how real restocking decisions are made.

---

## Demo Credentials

| Username | Password | Role |
|---|---|---|
| `admin` | `Admin1234!` | Full access — users, products, audit log |
| `manager` | `Manager1234!` | Products CRUD, audit log — no user management |
| `staff` | `Staff1234!` | Read-only — forecasts and products |

---

## Production Deployment

```bash
pip install -r requirements/production.txt

# Windows
set DJANGO_SETTINGS_MODULE=core.settings.production

# Mac/Linux
export DJANGO_SETTINGS_MODULE=core.settings.production

python manage.py collectstatic --noinput
gunicorn core.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

---

## Planned Features

- [ ] LLM Daily Brief — plain-English inventory summary generated from forecast data
- [ ] Purchase Order Draft + Approval Queue — AI proposes, Manager/Admin approves
- [ ] Conversational Q&A endpoint — RAG-style: Django fetches context, LLM answers
- [ ] Automated test suite — permission coverage + forecast edge cases
- [ ] OpenAPI/Swagger docs via `drf-spectacular`
- [ ] Rate limiting on auth endpoints
- [ ] Celery Beat scheduled forecast regeneration

---

## Related Repos

- **Frontend**: [hammi837/Invento-FE](https://github.com/hammi837/Invento-FE) — React dashboard

---

## License

MIT © 2026 Hammad
