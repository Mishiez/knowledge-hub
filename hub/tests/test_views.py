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


class PostCreateViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="creator", password="testpass123"
        )

    def test_post_create_valid_post_redirects_and_saves(self):
        response = self.client.post(
            "/posts/new/",
            {
                "title": "Created Via Test",
                "slug": "created-via-test",
                "content": "Some content written in a test.",
                "author": self.user.id,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/posts/created-via-test/")

        post = Post.objects.get(slug="created-via-test")
        self.assertEqual(post.title, "Created Via Test")
        self.assertEqual(post.author_id, self.user.id)


class PostListNPlusOneTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="author1", password="pass123")
        self.user2 = User.objects.create_user(username="author2", password="pass123")
        Post.objects.create(author=self.user1, title="Post One", slug="post-one", content="Content one")
        Post.objects.create(author=self.user2, title="Post Two", slug="post-two", content="Content two")

    def test_post_list_uses_bounded_query_count(self):
        with self.assertNumQueries(1):
            response = self.client.get("/")
            list(response.context["posts"])
            for post in response.context["posts"]:
                _ = post.author.username

        self.assertEqual(response.status_code, 200)

class PostDetailNPlusOneTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="detailauthor1", password="pass123")
        self.user2 = User.objects.create_user(username="detailauthor2", password="pass123")
        self.post = Post.objects.create(
            author=self.user1, title="NPlusOne Post", slug="nplusone-post", content="Content"
        )
        Comment.objects.create(post=self.post, author=self.user1, body="First comment")
        Comment.objects.create(post=self.post, author=self.user2, body="Second comment")

    def test_post_detail_uses_bounded_query_count(self):
        with self.assertNumQueries(2):
            response = self.client.get(f"/posts/{self.post.slug}/")
            list(response.context["comments"])
            for comment in response.context["comments"]:
                _ = comment.author.username

        self.assertEqual(response.status_code, 200)