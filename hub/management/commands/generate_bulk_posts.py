import random
from datetime import timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from hub.models import Post


class Command(BaseCommand):
    help = "Generate a large number of Post rows for query performance testing."

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=50000,
            help="Number of posts to generate (default: 50000).",
        )

    def handle(self, *args, **options):
        count = options["count"]

        users = list(User.objects.all())
        if not users:
            self.stdout.write(self.style.ERROR(
                "No users exist. Run 'python manage.py seed_data' first."
            ))
            return

        now = timezone.now()
        batch_size = 5000
        posts = []

        self.stdout.write(f"Generating {count} posts...")

        for i in range(count):
            random_days_ago = random.randint(0, 730)
            created_at = now - timedelta(
                days=random_days_ago,
                seconds=random.randint(0, 86400),
            )
            posts.append(Post(
                author=random.choice(users),
                title=f"Bulk Post {i}",
                slug=f"bulk-post-{i}",
                content="Auto-generated content for query performance testing.",
                created_at=created_at,
            ))

            if len(posts) >= batch_size:
                Post.objects.bulk_create(posts)
                posts = []
                self.stdout.write(f"  ...{i + 1} created")

        if posts:
            Post.objects.bulk_create(posts)

        self.stdout.write(self.style.SUCCESS(f"Done. {count} posts created."))