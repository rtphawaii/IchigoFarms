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
![picture](https://i.imgur.com/7RClXzl.png)
Product Details
![picture](https://i.imgur.com/fLkUzqP.png)
Cart
![picture](https://i.imgur.com/lY0w3Sd.png)
Checkout
![picture](https://i.imgur.com/IGKDU4M.png)
Payment
![picture](https://i.imgur.com/BMi4lFS.png)

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



