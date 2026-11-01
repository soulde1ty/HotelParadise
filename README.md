# Hotel Paradise

**English** | [Русский](README.ru.md)

A student hotel website built with Django, SQLite and Bootstrap. Python 3.12 is recommended; the project uses Django 5.2 LTS.

## Run locally

From the project root:

```bash
python -m venv .venv
```

Activate the environment on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

On macOS / Linux:

```bash
source .venv/bin/activate
```

Install dependencies and start the application:

```bash
pip install -r requirements.txt
python hotel_paradise/manage.py migrate
python hotel_paradise/manage.py seed_demo
python hotel_paradise/manage.py createsuperuser
python hotel_paradise/manage.py runserver
```

Website: http://127.0.0.1:8000/  
Administration: http://127.0.0.1:8000/admin/

`seed_demo` adds three rooms with photos included in the project. Repeating it fills missing Russian translations for unchanged demo content, preserving custom translations and descriptions. Create your own administrator password using `createsuperuser`; there is no shared password.

## English and Russian

The **EN / RU** switch is at the top of every page, including on mobile. It remembers your preference in a cookie and preserves the current page and search parameters. On the first visit, the browser language is used when supported; English is the fallback.

Navigation, pages, forms, validation errors, confirmations and administration labels are translated. Rooms have English and Russian title and description fields. If a Russian field is empty, its English value is displayed. Guest names and submitted messages remain as entered.

Interface translations live in `hotel_paradise/locale/ru/LC_MESSAGES/django.po`. The compiled `django.mo` is included, so no extra translation tools are needed to run the site. To edit translations, install GNU gettext and run these commands from `hotel_paradise`:

```bash
python manage.py makemessages -l ru
python manage.py compilemessages
```

Restart the server after compiling translations. When updating from the previous version, run `migrate` and `seed_demo` to add the language fields and demo translations.

## Features

- Home page, room catalog and room detail pages.
- Search by stay dates, bedroom count and bathroom count.
- Booking validation, availability checks and prevention of overlapping confirmed bookings.
- Server-side price calculation: price per night × number of nights.
- Confirmation with the booking number and total.
- A contact form that saves guest messages for staff to read in the admin.
- Room, booking and guest message management through Django Admin.
- Booking cancellation through the Cancelled status or the Cancel selected bookings action.
- Room image uploads and a fallback image when no photo is available.

`Room.available` means that a room is open for bookings. Occupancy is determined from confirmed booking dates. Check-out day is free for the next guest to arrive. Cancellation releases the dates and keeps the booking record.

Special requests are optional. Search dates are passed to the booking form. Refreshing the confirmation destination does not create another booking.

## Project structure

All application directories below are inside `hotel_paradise/`:

- `hotel_paradise/` — settings and URL routes.
- `room/` — rooms, search, detail pages and the demo data command.
- `booking/` — models, forms, date validation and bookings.
- `contact/` — guest messages.
- `main/`, `about/`, `service/`, `team/`, `testimonial/` — website pages.
- `templates/` — shared layout, form fields and room cards.
- `static/` — CSS, JavaScript and images.
- `locale/` — Russian interface translations.

## Checks

Run from the project root:

```bash
python hotel_paradise/manage.py check
python hotel_paradise/manage.py makemigrations --check --dry-run
python hotel_paradise/manage.py test hotel_paradise/
```

Tests cover bookings, date overlaps, cancellation, pricing, search, contact submissions, CSRF protection, pages and both languages. They use a separate test database.

## Existing databases

Back up `hotel_paradise/db.sqlite3` and uploaded photos before running migrations. Invalid legacy bookings with check-out on or before check-in, or negative prices, must be corrected before migrating because the new database constraints reject them. Existing `static/img/...` image paths are supported.

The old application disabled Available after a booking. Review that flag in the admin after updating and enable rooms that are open to guests. The new booking flow checks date ranges and no longer disables that flag.

## Configuration and scope

Local DEBUG mode is enabled by default. Environment variables:

- `DJANGO_DEBUG=false` — disable debug mode.
- `DJANGO_SECRET_KEY` — your secret key; required when debug is disabled.
- `DJANGO_ALLOWED_HOSTS` — comma-separated hostnames; defaults to localhost and loopback addresses.

A `.env` file is not loaded automatically. Set variables in your shell or hosting settings. Deployment also requires a WSGI/ASGI server, HTTPS, static/media serving and backups. Django's `runserver` is for development.

Payments and email delivery are not connected. Contact messages are stored in the admin. Team, service and review sections contain demonstration content; replace it, along with contact details and photos, before using the site for a real hotel. Bootstrap JavaScript, fonts and icons are loaded from external CDNs.

The design is based on the original HTML Codex template. Author attribution links remain in the footer.
