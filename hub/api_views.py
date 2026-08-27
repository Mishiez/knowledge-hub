from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Post, Comment
from .serializers import CommentSerializer
from .serializers import PostSerializer
from .permissions import IsOwnerOrReadOnly
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from .permissions import IsOwnerOrReadOnly



class PostListView(generics.ListCreateAPIView):
    queryset = Post.objects.select_related("author")
    serializer_class = PostSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.select_related("author")
    serializer_class = PostSerializer
    lookup_field = "slug"
    permission_classes = [IsOwnerOrReadOnly]


class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Comment.objects.filter(post_id=self.kwargs['post_id']).select_related('author')

    def perform_create(self, serializer):
        post = Post.objects.get(pk=self.kwargs['post_id'])
        serializer.save(author=self.request.user, post=post)


class CommentDeleteView(generics.DestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsOwnerOrReadOnly]

class StandardPagination(PageNumberPagination):
    page_size = 10


class PostListView(generics.ListCreateAPIView):
    queryset = Post.objects.select_related('author')
    serializer_class = PostSerializer
    pagination_class = StandardPagination  # was pagination_class = None

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class PostListView(generics.ListCreateAPIView):
    queryset = Post.objects.select_related('author')
    serializer_class = PostSerializer
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['author__username']
    search_fields = ['title']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)