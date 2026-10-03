# LocalLink

A community-support marketplace that connects people who need a hand — with
technology, transport, gardening, tutoring or companionship — to trusted
university students and local volunteers nearby.

Built with **Python / Django** as the prototype deliverable for
PRT551 Project Management, Risk & Reliability.

## Features
- Custom user accounts with three roles: **Support Seeker**, **Helper / Volunteer**, **Coordinator**
- Seekers post **help requests** (category, location, urgency, remote-OK)
- Helpers browse/filter requests and **offer to help**
- Seekers review offers and **accept a helper** (auto-declines the rest)
- Built-in **messaging** between the matched pair
- **Mark complete** then leave a **1–5 star review**; profiles show average ratings
- **Coordinator dashboard** + Django admin for verification and moderation
- Seed command with demo categories, users and requests

## Quick start
```bash
# 1. (optional) create a virtual environment
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 2. install dependencies
pip install -r requirements.txt

# 3. create the database
python manage.py migrate

# 4. load demo data (creates admin + sample users/requests)
python manage.py seed_data

# 5. run the server
python manage.py runserver
```
Then open http://127.0.0.1:8000/

## Demo logins
| Role | Username | Password |
|------|----------|----------|
| Coordinator / admin | `admin` | `adminpass123` |
| Seeker | `margaret` | `password123` |
| Helper | `aisha` | `password123` |

Admin site: http://127.0.0.1:8000/admin/

## Project layout
```
locallink/            project settings & root urls
accounts/             custom user model, auth, profiles, dashboard
core/                 categories, help requests, offers, reviews, messages
templates/            Bootstrap 5 templates
```
