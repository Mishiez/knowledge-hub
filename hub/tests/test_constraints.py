from django.contrib.auth.models import User
from django.db import IntegrityError, transaction, connection
from django.test import TestCase

from hub.models import Post, Comment


class DatabaseConstraintTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="constraintuser", password="pass123")
        self.post = Post.objects.create(
            author=self.user, title="Base Post", slug="base-post", content="Content"
        )

    def test_duplicate_slug_rejected_at_db_level(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Post.objects.create(
                    author=self.user, title="Dup", slug="base-post", content="Other"
                )

    def test_comment_with_nonexistent_post_id_rejected(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Comment.objects.create(post_id=999999, author=self.user, body="Orphan")
                connection.check_constraints()

    def test_post_missing_author_rejected_at_db_level(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Post.objects.create(
                    author=None, title="No Author", slug="no-author", content="X"
                )