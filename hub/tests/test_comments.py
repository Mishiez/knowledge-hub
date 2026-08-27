from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from hub.models import Post, Comment


class CommentAPITests(APITestCase):
    def setUp(self):
        self.michelle = User.objects.create_user(username='michelle', password='testpass123')
        self.john = User.objects.create_user(username='john', password='testpass123')
        self.post = Post.objects.create(
            author=self.michelle, title='Test Post', slug='test-post', content='Content'
        )
        self.comment = Comment.objects.create(
            post=self.post, author=self.michelle, body='First comment'
        )
        self.list_url = reverse('api-comment-list-create', kwargs={'post_id': self.post.id})
        self.delete_url = reverse('api-comment-delete', kwargs={'pk': self.comment.id})

    def test_list_comments_public(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_comment_authenticated(self):
        self.client.force_authenticate(user=self.john)
        response = self.client.post(self.list_url, {'body': 'A new comment'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 2)

    def test_create_comment_unauthenticated_fails(self):
        response = self.client.post(self.list_url, {'body': 'Should fail'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_comment_validation_failure(self):
        self.client.force_authenticate(user=self.john)
        response = self.client.post(self.list_url, {'body': ''})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_owner_can_delete_comment(self):
        self.client.force_authenticate(user=self.michelle)
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Comment.objects.filter(id=self.comment.id).exists())

    def test_non_owner_cannot_delete_comment(self):
        self.client.force_authenticate(user=self.john)
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Comment.objects.filter(id=self.comment.id).exists())

    def test_delete_nonexistent_comment_404(self):
        self.client.force_authenticate(user=self.michelle)
        url = reverse('api-comment-delete', kwargs={'pk': 9999})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)