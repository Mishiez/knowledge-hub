from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from hub.models import Post


class PostAPITests(APITestCase):
    def setUp(self):
        self.michelle = User.objects.create_user(username='michelle', password='testpass123')
        self.john = User.objects.create_user(username='john', password='testpass123')
        self.post = Post.objects.create(
            author=self.michelle, title='Original Title', slug='original-title', content='Content'
        )
        self.list_url = reverse('api-post-list')
        self.detail_url = reverse('api-post-detail', kwargs={'slug': self.post.slug})

    def test_list_posts_public(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIsInstance(response.data['results'], list)

    def test_retrieve_post_public(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Original Title')

    def test_retrieve_nonexistent_post_404(self):
        url = reverse('api-post-detail', kwargs={'slug': 'does-not-exist'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_post_authenticated(self):
        self.client.force_authenticate(user=self.john)
        response = self.client.post(self.list_url, {
            'title': 'New Post', 'slug': 'new-post', 'content': 'New content'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['author'], 'john')

    def test_create_post_unauthenticated_fails(self):
        response = self.client.post(self.list_url, {
            'title': 'New Post', 'slug': 'new-post', 'content': 'New content'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_post_validation_failure(self):
        self.client.force_authenticate(user=self.john)
        response = self.client.post(self.list_url, {'title': '', 'slug': '', 'content': ''})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_owner_can_update_post(self):
        self.client.force_authenticate(user=self.michelle)
        response = self.client.patch(self.detail_url, {'title': 'Updated Title'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, 'Updated Title')

    def test_non_owner_cannot_update_post(self):
        self.client.force_authenticate(user=self.john)
        response = self.client.patch(self.detail_url, {'title': 'Hacked Title'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, 'Original Title')

    def test_non_owner_cannot_delete_post(self):
        self.client.force_authenticate(user=self.john)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Post.objects.filter(id=self.post.id).exists())

    def test_owner_can_delete_post(self):
        self.client.force_authenticate(user=self.michelle)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Post.objects.filter(id=self.post.id).exists())

    def test_create_post_duplicate_slug_returns_clean_400(self):
        self.client.force_authenticate(user=self.john)
        response = self.client.post(self.list_url, {
            'title': 'Another Post', 'slug': 'original-title', 'content': 'Content'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('slug', response.data)