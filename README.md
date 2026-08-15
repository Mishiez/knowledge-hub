# Knowledge Hub

A knowledge-sharing platform where users publish posts and readers (including the author) discuss them through comments.

## Tech stack

- Python 3.12
- Django 5.1
- SQLite (dev)
- python-dotenv for environment variable loading

## Setup

1. Clone the repo and enter the project folder:
   ```bash
   git clone <repo-url>
   cd knowledge-hub
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create your `.env` file from the example, and set a real `SECRET_KEY`:
   ```bash
   cp .env.example .env
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```
   Paste the generated key into `.env` as the value for `SECRET_KEY`.

5. Run migrations:
   ```bash
   python manage.py migrate
   ```

6. Create a superuser (for admin access):
   ```bash
   python manage.py createsuperuser
   ```

7. Run the development server:
   ```bash
   python manage.py runserver
   ```

   Visit `http://127.0.0.1:8000/` for the post list, and `http://127.0.0.1:8000/admin/` for the admin panel.

## Running tests

```bash
python manage.py test hub
```

## Project structure

```
knowledgehub/
├── config/
│   ├── settings/
│   │   ├── base.py     # shared settings
│   │   ├── dev.py      # DEBUG=True, local settings
│   │   └── prod.py     # DEBUG=False, production settings
│   └── urls.py
└── hub/
    ├── models.py        # Post, Comment
    ├── views.py         # post_list, post_detail, post_create
    ├── urls.py
    ├── admin.py
    ├── tests/
    │   ├── test_models.py
    │   └── test_views.py
    └── templates/hub/
```

## Notes

- `post_create` has no authentication yet — the form includes a manual author dropdown as a placeholder, since real user sessions/login aren't implemented.
- Department/Topic filtering and search are planned as future work.