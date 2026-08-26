from rest_framework import generics
from .models import Post
from .serializers import PostSerializer


class PostListView(generics.ListCreateAPIView):
    queryset = Post.objects.select_related("author")
    serializer_class = PostSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.select_related("author")
    serializer_class = PostSerializer
    lookup_field = "slug"