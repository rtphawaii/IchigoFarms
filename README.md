# Ichigo Farms Store

A Django-based ecommerce site with:
- Product catalog
- Cart & guest checkout
- Stripe payments
- Order confirmation + shipping emails
- Admin order management

## Tech stack
- Django
- Stripe Checkout
- Tailwind CSS
- PostgreSQL / SQLite
- Gunicorn + Nginx (production)

## Local setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver
