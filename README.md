# Ichigo Farms Store

A Django-based ecommerce site with:
- Product catalog
- Cart & guest checkout
- Stripe payments
- Order confirmation + shipping emails
- Admin order management (inventory, order processing, adding/modifying products)

## DEMO
video: https://vimeo.com/1151267270?fl=ip&fe=ec

Store
![picture](https://imgur.com/a/WO4B4Wl)
Product Details
![picture](https://imgur.com/a/vLyxdGH)
Cart
![picture](https://imgur.com/a/acUHIIE)
Checkout
![picture](https://imgur.com/a/oAenYbs)
Payment
![picture](https://imgur.com/a/GVQNTp1)

## Tech stack
- Django
- Stripe Checkout
- Brevo Email
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
```



