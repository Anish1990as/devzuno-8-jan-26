
# Devzuno Technologies — Django + Bootstrap Starter

A starter template implementing:
- Public site: Home, Pricing, Portfolio, Reviews, Contact
- Client Area: Login/Register, Dashboard, Profile (address/phone editable), Services, Domains (demo availability UI), Invoices/Quotes, Open Ticket, Projects Overview
- Order → Invoice → Razorpay (demo link, easily switch to live)
- Admin-manageable content: Pricing plans, Portfolio, Testimonials, Departments, Projects, Site Settings
- WhatsApp (+919219317352) & support@devzuno.com defaults in Site Settings (editable in admin)

## Quick Start

```bash
python -m venv env
# Windows: env\Scripts\activate
# Linux/Mac: source env/bin/activate
pip install -r requirements.txt

# Initial setup
python manage.py migrate
python manage.py createsuperuser  # create admin user
python manage.py loaddata seed.json  # optional demo content

# Run
python manage.py runserver
```

Admin: `/admin/`  
Client Area: `/client/` (login/register), `/dashboard/` (after login)

## Switch Razorpay to live
Update **Site Settings** in admin: `Payment Mode = live` and set `razorpay_key_id` / `razorpay_key_secret`.
The demo button uses a placeholder URL; replace it in template or via Site Settings.

## Tech
- Django 5
- Bootstrap 5 (CDN)
- SQLite (default)
- HTML/CSS/JS (no Tailwind)
