# Knowledge Hub

A knowledge-sharing platform where users publish posts and readers (including the author) discuss them through comments.

## Tech stack

- Python 3.12
- Django 5.1
- PostgreSQL
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

4. Create a PostgreSQL database and user:
   ```bash
   sudo -u postgres psql
   ```
   ```sql
   CREATE DATABASE knowledgehub;
   CREATE USER khuser WITH PASSWORD 'your-password-here';
   \c knowledgehub
   GRANT ALL ON SCHEMA public TO khuser;
   ALTER DATABASE knowledgehub OWNER TO khuser;
   ALTER USER khuser CREATEDB;
   \q
   ```
   The `CREATEDB` privilege is required because Django's test runner creates and destroys a temporary test database on each run.

5. Create your `.env` file from the example, and fill in real values:
   ```bash
   cp .env.example .env
   ```
   Set `SECRET_KEY` (generate one below), and set `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` to match what you created in step 4.
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

6. Run migrations:
   ```bash
   python manage.py migrate
   ```

7. (Optional) Seed the database with realistic sample data:
   ```bash
   python manage.py seed_data
   ```
   This creates a handful of sample users, posts, and comments.

8. Create a superuser (for admin access):
   ```bash
   python manage.py createsuperuser
   ```

9. Run the development server:
   ```bash
   python manage.py runserver
   ```

   Visit `http://127.0.0.1:8000/` for the post list, and `http://127.0.0.1:8000/admin/` for the admin panel.

## Running tests

```bash
python manage.py test hub
```

Tests cover model creation, relationships, and database-level constraints (unique slugs, foreign key enforcement, required fields), plus view status codes and content.

## Project structure

```
knowledgehub/
├── config/
│   ├── settings/
│   │   ├── base.py     # shared settings
│   │   ├── dev.py      # DEBUG=True, local settings
│   │   └── prod.py     # DEBUG=False, production settings
└── hub/
    ├── models.py           # Post, Comment
    ├── views.py            # post_list, post_detail, post_create
    ├── urls.py
    ├── admin.py
    ├── management/
    │   └── commands/
    │       └── seed_data.py
    ├── tests/
    │   ├── test_models.py
    │   ├── test_views.py
    │   └── test_constraints.py
    └── templates/hub/
```

## Notes

- `post_create` has no authentication yet — the form includes a manual author dropdown as a placeholder, since real user sessions/login aren't implemented.
- Department/Topic filtering and search are planned as future work.