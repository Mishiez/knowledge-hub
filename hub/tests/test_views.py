from django.contrib.auth.models import User
from django.test import TestCase

from hub.models import Post, Comment


class PostListViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="viewauthor", password="testpass123"
        )
        self.post = Post.objects.create(
            author=self.user,
            title="A Known Post Title",
            slug="a-known-post",
            content="Some content.",
        )

    def test_post_list_status_and_content(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "A Known Post Title")


class PostDetailViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="viewauthor2", password="testpass123"
        )
        self.post = Post.objects.create(
            author=self.user,
            title="Detail Post",
            slug="detail-post",
            content="Unique detail content here.",
        )
        self.comment = Comment.objects.create(
            post=self.post, author=self.user, body="A visible comment body"
        )

    def test_post_detail_valid_slug_status_and_content(self):
        response = self.client.get("/posts/detail-post/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Unique detail content here.")
        self.assertContains(response, "A visible comment body")

    def test_post_detail_invalid_slug_returns_404(self):
        response = self.client.get("/posts/does-not-exist/")
        self.assertEqual(response.status_code, 404)