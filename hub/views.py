from django.shortcuts import render, get_object_or_404
from .models import Post


def post_list(request):
    posts = Post.objects.all()
    return render(request, "hub/post_list.html", {"posts": posts})


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    comments = post.comments.all()
    return render(request, "hub/post_detail.html", {"post": post, "comments": comments})