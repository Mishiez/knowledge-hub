from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from hub.models import Post, Like


class LikeAPITests(APITestCase):
    def setUp(self):
        self.michelle = User.objects.create_user(username='michelle', password='testpass123')
        self.john = User.objects.create_user(username='john', password='testpass123')
        self.post = Post.objects.create(
            author=self.michelle, title='Test Post', slug='test-post', content='Content'
        )
        self.like_url = reverse('api-post-like-toggle', kwargs={'post_id': self.post.id})

    def test_like_requires_authentication(self):
        response = self.client.post(self.like_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_can_like_post(self):
        self.client.force_authenticate(user=self.john)
        response = self.client.post(self.like_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['liked'])
        self.assertEqual(response.data['like_count'], 1)
        self.assertTrue(Like.objects.filter(post=self.post, user=self.john).exists())

    def test_liking_twice_toggles_unlike(self):
        self.client.force_authenticate(user=self.john)
        self.client.post(self.like_url)
        response = self.client.post(self.like_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['liked'])
        self.assertEqual(response.data['like_count'], 0)
        self.assertFalse(Like.objects.filter(post=self.post, user=self.john).exists())