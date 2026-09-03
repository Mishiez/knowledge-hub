# Knowledge Hub

A knowledge-sharing platform where users publish posts and readers (including the author) discuss them through comments, and can like posts they find useful.

## Tech stack

- Python 3.12
- Django 5.1
- PostgreSQL
- python-dotenv for environment variable loading
- Docker + Docker Compose for containerized local development

## Running with Docker (recommended)

The whole stack (backend, frontend, PostgreSQL) can be brought up with one command.

1. Clone both repos as sibling folders:
   ```bash
   git clone <backend-repo-url> knowledge-hub
   git clone <frontend-repo-url> knowledge-hub-frontend
   ```

2. In the backend repo, create a `.env` file (gitignored — never committed):
   ```
   SECRET_KEY=<generate one, see below>
   DB_NAME=knowledgehub
   DB_USER=khuser
   DB_PASSWORD=your-password-here
   ```
   Generate a secret key:
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```
   Avoid `$` characters in the value — Docker Compose interprets `$` as the start of a variable reference.

3. Build and start everything:
   ```bash
   docker compose up --build
   ```
   This starts PostgreSQL, runs migrations automatically, starts the Django backend on `http://localhost:8000`, and starts the frontend on `http://localhost:5173`.

4. (Optional) Seed sample data inside the running container:
   ```bash
   docker compose exec backend python manage.py seed_data
   ```

5. Run the test suite inside the container (proves parity with local test runs):
   ```bash
   docker compose exec backend python manage.py test
   ```

6. Tear down, including the database volume, for a completely clean slate:
   ```bash
   docker compose down -v
   ```

### Container architecture

- **`db`** — PostgreSQL 16, data persisted in a named volume so it survives container restarts (removed only via `down -v`)
- **`backend`** — Django, waits for `db`'s healthcheck before running migrations and starting the server, binds `0.0.0.0:8000` so it's reachable from outside the container
- **`frontend`** — multi-stage build: a Node stage runs `npm run build`, then only the resulting static files are copied into a minimal nginx image — no Node runtime or dev dependencies ship in the final image
- All secrets and credentials are read from the gitignored `.env` file via Compose variable substitution — never hardcoded in a Dockerfile or `docker-compose.yml`

## Running locally without Docker

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

Tests cover model creation, relationships, database-level constraints (unique slugs, foreign key enforcement, required fields), view status codes and content, the full REST API (success/validation/auth/ownership/not-found per endpoint), and the like/unlike toggle.

## Project structure

```
knowledgehub/
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── config/
│   ├── settings/
│   │   ├── base.py     # shared settings
│   │   ├── dev.py      # DEBUG=True, local settings
│   │   └── prod.py     # DEBUG=False, production settings
└── hub/
    ├── models.py           # Post, Comment, Like
    ├── views.py            # post_list, post_detail, post_create
    ├── api_views.py        # DRF views: posts, comments, likes
    ├── serializers.py
    ├── permissions.py      # IsOwnerOrReadOnly
    ├── urls.py
    ├── api_urls.py
    ├── admin.py
    ├── management/
    │   └── commands/
    │       ├── seed_data.py
    │       └── generate_bulk_posts.py
    ├── tests/
    │   ├── test_models.py
    │   ├── test_views.py
    │   ├── test_constraints.py
    │   ├── test_posts.py
    │   ├── test_comments.py
    │   └── test_likes.py
    └── templates/hub/
```

## API (Django REST Framework)

Base URL: `http://127.0.0.1:8000/api/`

### Authentication (token-based)
- `POST /api/auth/register/` — `{username, email, password}` → 201, returns `{user, token}`
- `POST /api/auth/login/` — `{username, password}` → 200, returns `{user, token}`
- `POST /api/auth/logout/` — requires token → 204
- `GET /api/auth/me/` — requires token → 200, current user

Authenticated requests need header: `Authorization: Token <token>`

### Posts
- `GET /api/posts/` — public, paginated (`{count, next, previous, results}`), supports `?search=` (title) and `?author__username=`
- `POST /api/posts/` — requires token
- `GET /api/posts/<slug>/` — public
- `PATCH`/`DELETE /api/posts/<slug>/` — requires token + ownership

### Comments
- `GET`/`POST /api/posts/<post_id>/comments/` — GET public, POST requires token
- `DELETE /api/comments/<id>/` — requires token + ownership

### Likes
- `POST /api/posts/<post_id>/like/` — requires token, toggles like/unlike, returns `{liked, like_count}`

Non-owners attempting to modify/delete another user's post or comment receive `403 Forbidden`.

## Notes

- `post_create` (the legacy template view) has no authentication — the form includes a manual author dropdown as a placeholder, since the API's real auth flow now handles this for the frontend instead.
- Topic filtering beyond author/title search is planned as future work.