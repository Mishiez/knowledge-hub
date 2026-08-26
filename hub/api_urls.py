from django.urls import path
from . import auth_views
from rest_framework.generics import ListAPIView, RetrieveAPIView
from .models import Post
from .serializers import PostSerializer

class PostListView(ListAPIView):
    queryset = Post.objects.select_related("author")
    serializer_class = PostSerializer
    pagination_class = None


class PostDetailView(RetrieveAPIView):
    queryset = Post.objects.select_related("author")
    serializer_class = PostSerializer
    lookup_field = "slug"

urlpatterns = [
    path("auth/register/", auth_views.RegisterView.as_view(), name="register"),
    path("auth/login/", auth_views.LoginView.as_view(), name="login"),
    path("auth/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("auth/me/", auth_views.MeView.as_view(), name="me"),
    path("posts/", PostListView.as_view(), name="api-post-list"),
    path("posts/<slug:slug>/", PostDetailView.as_view(), name="api-post-detail"),
]

