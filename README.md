# 🛍️ Django E-Commerce Backend

A full-featured REST API backend built with Django + DRF + Stripe.

## Project Structure

```
ecommerce/
├── config/
│   ├── settings.py
│   └── urls.py
├── apps/
│   ├── users/       # Auth, JWT, Addresses
│   ├── products/    # Catalog, Categories, Reviews
│   ├── cart/        # Cart management
│   ├── orders/      # Order lifecycle
│   └── payments/    # Stripe integration
├── manage.py
└── requirements.txt
```

## Setup

```bash
# 1. Create virtual environment
python -m venv venv && source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create .env file
cp .env.example .env   # edit with your keys

# 4. Run migrations
python manage.py makemigrations users products cart orders payments
python manage.py migrate

# 5. Create superuser
python manage.py createsuperuser

# 6. Start server
python manage.py runserver
```

## .env.example

```
SECRET_KEY=django-insecure-change-me
DEBUG=True
ALLOWED_HOSTS=*
CORS_ALLOWED_ORIGINS=http://localhost:3000

STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

---

## API Endpoints

### 🔐 Auth  `POST /api/v1/auth/`

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/register/` | No | Create account |
| POST | `/login/` | No | Get JWT tokens |
| POST | `/token/refresh/` | No | Refresh access token |
| GET/PATCH | `/me/` | Yes | Get / update profile |
| GET/POST | `/addresses/` | Yes | List / create addresses |
| GET/PATCH/DELETE | `/addresses/<id>/` | Yes | Manage address |

---

### 📦 Products  `GET /api/v1/products/`

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/` | No | List products (filter/search/sort) |
| POST | `/` | Admin | Create product |
| GET | `/<slug>/` | No | Product detail |
| PATCH | `/<slug>/` | Admin | Update product |
| DELETE | `/<slug>/` | Admin | Delete product |
| GET/POST | `/<slug>/reviews/` | No/Yes | Reviews |
| GET | `/categories/` | No | List categories |
| GET | `/categories/<slug>/` | No | Category detail |

**Query params for product list:**
- `search=` — search name/description
- `category=` — filter by category slug
- `min_price=`, `max_price=` — price range
- `is_featured=true` — featured only
- `ordering=price` / `ordering=-created_at`

---

### 🛒 Cart  `/api/v1/cart/`

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/` | Yes | Get current cart |
| POST | `/add/` | Yes | Add item `{variant_id, quantity}` |
| PATCH | `/items/<id>/` | Yes | Update quantity `{quantity}` |
| DELETE | `/items/<id>/remove/` | Yes | Remove item |
| DELETE | `/clear/` | Yes | Empty cart |

---

### 📋 Orders  `/api/v1/orders/`

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/` | Yes | List my orders |
| POST | `/create/` | Yes | Create from cart `{shipping_address_id}` |
| GET | `/<id>/` | Yes | Order detail |
| POST | `/<id>/cancel/` | Yes | Cancel order |

**Order flow:** Cart → `POST /orders/create/` → Pay via Stripe → Order confirmed

---

### 💳 Payments  `/api/v1/payments/`

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/create-intent/` | Yes | Create Stripe PaymentIntent `{order_id}` |
| POST | `/confirm/` | Yes | Confirm after frontend payment `{payment_intent_id}` |
| POST | `/webhook/` | No | Stripe webhook receiver |

**Payment flow:**
1. `POST /payments/create-intent/` → get `client_secret`
2. Frontend completes payment with Stripe.js using `client_secret`
3. `POST /payments/confirm/` with `payment_intent_id`
4. OR Stripe fires webhook to `/payments/webhook/` (recommended for production)

---

## Key Features

- ✅ Custom User model (email-based auth)
- ✅ JWT authentication with refresh tokens
- ✅ Product variants (size/color) with stock tracking
- ✅ Cart with stock validation
- ✅ Order creation with tax + shipping calculation
- ✅ Order cancellation with stock restock
- ✅ Stripe PaymentIntents
- ✅ Stripe webhook handling (succeeded, failed, refunded)
- ✅ Product reviews (one per user)
- ✅ Address management
- ✅ Admin panel for all models
- ✅ Filtering, searching, and pagination
