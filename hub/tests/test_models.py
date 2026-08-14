from django.contrib.auth.models import User
from django.db import IntegrityError
from django.test import TestCase

from hub.models import Post, Comment


class PostModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="author1", password="testpass123"
        )

    def test_create_valid_post(self):
        post = Post.objects.create(
            author=self.user,
            title="First Post",
            slug="first-post",
            content="Some content here.",
        )
        self.assertEqual(post.title, "First Post")
        self.assertEqual(post.slug, "first-post")
        self.assertEqual(post.author, self.user)

    def test_post_author_relationship(self):
        post = Post.objects.create(
            author=self.user,
            title="Second Post",
            slug="second-post",
            content="More content.",
        )
        self.assertIn(post, self.user.posts.all())

    def test_duplicate_slug_raises_integrity_error(self):
        Post.objects.create(
            author=self.user,
            title="Original",
            slug="same-slug",
            content="Content A",
        )
        with self.assertRaises(IntegrityError):
            Post.objects.create(
                author=self.user,
                title="Duplicate",
                slug="same-slug",
                content="Content B",
            )

    def test_deleting_post_cascades_to_comments(self):
        post = Post.objects.create(
            author=self.user,
            title="Cascade Post",
            slug="cascade-post",
            content="Content",
        )
        comment = Comment.objects.create(
            post=post, author=self.user, body="A comment"
        )
        post_id = post.id
        comment_id = comment.id

        post.delete()

        self.assertFalse(Post.objects.filter(id=post_id).exists())
        self.assertFalse(Comment.objects.filter(id=comment_id).exists())

    def test_deleting_user_cascades_to_posts_and_comments(self):
        post = Post.objects.create(
            author=self.user,
            title="User Cascade Post",
            slug="user-cascade-post",
            content="Content",
        )
        comment = Comment.objects.create(
            post=post, author=self.user, body="A comment"
        )
        post_id = post.id
        comment_id = comment.id

        self.user.delete()

        self.assertFalse(Post.objects.filter(id=post_id).exists())
        self.assertFalse(Comment.objects.filter(id=comment_id).exists())


class CommentModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="author2", password="testpass123"
        )
        self.post = Post.objects.create(
            author=self.user,
            title="Post For Comments",
            slug="post-for-comments",
            content="Content",
        )

    def test_create_comment_linked_to_post(self):
        comment = Comment.objects.create(
            post=self.post, author=self.user, body="Nice post!"
        )
        self.assertEqual(comment.post, self.post)
        self.assertEqual(comment.body, "Nice post!")

    def test_post_comments_relationship(self):
        comment = Comment.objects.create(
            post=self.post, author=self.user, body="Another comment"
        )
        self.assertIn(comment, self.post.comments.all())