from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from hub.models import Post, Comment


class Command(BaseCommand):
    help = 'Seeds the database with realistic development users, posts, and comments.'

    def handle(self, *args, **options):
        users_data = [
            {'username': 'michelle', 'email': 'michelle@example.com'},
            {'username': 'john', 'email': 'john@example.com'},
            {'username': 'jane', 'email': 'jane@example.com'},
            {'username': 'david', 'email': 'david@example.com'},
        ]

        users = {}
        for u in users_data:
            user, created = User.objects.get_or_create(
                username=u['username'], defaults={'email': u['email']}
            )
            if created:
                user.set_password('devpass123')
                user.save()
            users[u['username']] = user
            self.stdout.write(f"{'Created' if created else 'Found'} user: {u['username']}")

        posts_data = [
            ('michelle', 'Understanding Django Models', 'understanding-django-models',
             'Django models map Python classes to database tables, handling the ORM layer for you.'),
            ('michelle', 'Why APIs Matter', 'why-apis-matter',
             'APIs let frontend and backend evolve independently as long as the contract holds.'),
            ('john', 'PostgreSQL Explained', 'postgresql-explained',
             'PostgreSQL is a powerful open-source relational database with strong consistency guarantees.'),
            ('john', 'Database Design Basics', 'database-design-basics',
             'Good schema design starts with identifying entities and their relationships.'),
            ('jane', 'Introduction to REST APIs', 'introduction-to-rest-apis',
             'REST APIs use standard HTTP verbs to perform predictable operations on resources.'),
            ('david', 'Understanding Authentication', 'understanding-authentication',
             'Authentication verifies who a user is; authorization determines what they can do.'),
        ]

        posts = {}
        for username, title, slug, content in posts_data:
            post, created = Post.objects.get_or_create(
                slug=slug,
                defaults={'author': users[username], 'title': title, 'content': content},
            )
            posts[slug] = post
            self.stdout.write(f"{'Created' if created else 'Found'} post: {title}")

        comments_data = [
            ('understanding-django-models', 'john', 'This clarified a lot, thanks!'),
            ('understanding-django-models', 'jane', 'Would love a follow-up on migrations.'),
            ('postgresql-explained', 'michelle', 'Great intro for beginners.'),
            ('introduction-to-rest-apis', 'david', 'Clear and concise, appreciated.'),
        ]

        for slug, username, body in comments_data:
            Comment.objects.get_or_create(
                post=posts[slug], author=users[username], body=body
            )

        self.stdout.write(self.style.SUCCESS('Seed data created successfully.'))