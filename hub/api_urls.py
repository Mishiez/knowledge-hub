from django.urls import path
from . import auth_views
from .api_views import PostListView, PostDetailView, CommentListCreateView, CommentDeleteView, PostLikeToggleView

urlpatterns = [
    path("auth/register/", auth_views.RegisterView.as_view(), name="register"),
    path("auth/login/", auth_views.LoginView.as_view(), name="login"),
    path("auth/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("auth/me/", auth_views.MeView.as_view(), name="me"),
    path("posts/", PostListView.as_view(), name="api-post-list"),
    path("posts/<slug:slug>/", PostDetailView.as_view(), name="api-post-detail"),
    path('posts/<int:post_id>/comments/', CommentListCreateView.as_view(), name='api-comment-list-create'),
    path('comments/<int:pk>/', CommentDeleteView.as_view(), name='api-comment-delete'),
    path('posts/<int:post_id>/like/', PostLikeToggleView.as_view(), name='api-post-like-toggle'),
]
