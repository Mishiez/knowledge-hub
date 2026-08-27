from django.urls import path
from . import auth_views
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Post
from .serializers import PostSerializer
from .permissions import IsOwnerOrReadOnly
from .api_views import PostListView, PostDetailView, CommentListCreateView, CommentDeleteView

class PostListCreateView(ListCreateAPIView):
    queryset = Post.objects.select_related("author")
    serializer_class = PostSerializer
    pagination_class = None
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class PvenvostDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.select_related("author")
    serializer_class = PostSerializer
    lookup_field = "slug"
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]


urlpatterns = [
    path("auth/register/", auth_views.RegisterView.as_view(), name="register"),
    path("auth/login/", auth_views.LoginView.as_view(), name="login"),
    path("auth/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("auth/me/", auth_views.MeView.as_view(), name="me"),
    path("posts/", PostListCreateView.as_view(), name="api-post-list"),
    path("posts/<slug:slug>/", PostDetailView.as_view(), name="api-post-detail"),
    path('posts/<int:post_id>/comments/', CommentListCreateView.as_view(), name='api-comment-list-create'),
    path('comments/<int:pk>/', CommentDeleteView.as_view(), name='api-comment-delete'),
]