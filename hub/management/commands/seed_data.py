from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from hub.models import Post, Comment


class Command(BaseCommand):
    help = "Seed the database with realistic sample data."

    def handle(self, *args, **options):
        users_data = ["michelle", "john", "jane", "david"]
        users = []
        for username in users_data:
            user, _ = User.objects.get_or_create(
                username=username,
                defaults={"email": f"{username}@example.com"},
            )
            users.append(user)

        posts_data = [
            ("Understanding Django Models", "understanding-django-models"),
            ("Introduction to REST APIs", "introduction-to-rest-apis"),
            ("Why PostgreSQL Matters", "why-postgresql-matters"),
            ("Database Relationships Explained", "database-relationships-explained"),
        ]
        posts = []
        for i, (title, slug) in enumerate(posts_data):
            post, _ = Post.objects.get_or_create(
                slug=slug,
                defaults={
                    "author": users[i % len(users)],
                    "title": title,
                    "content": f"Sample content for {title}.",
                },
            )
            posts.append(post)

        Comment.objects.get_or_create(
            post=posts[0], author=users[1], defaults={"body": "Great explanation!"}
        )
        Comment.objects.get_or_create(
            post=posts[0], author=users[2], defaults={"body": "Very helpful, thanks."}
        )
        Comment.objects.get_or_create(
            post=posts[1], author=users[0], defaults={"body": "Looking forward to more on this."}
        )
        Comment.objects.get_or_create(
            post=posts[2], author=users[3], defaults={"body": "PostgreSQL is great indeed."}
        )

        self.stdout.write(self.style.SUCCESS("Seed data created successfully."))