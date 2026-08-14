from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
from .models import Post


def post_list(request):
    posts = Post.objects.all()
    return render(request, "hub/post_list.html", {"posts": posts})


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    comments = post.comments.all()
    return render(request, "hub/post_detail.html", {"post": post, "comments": comments})


def post_create(request):
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        slug = request.POST.get("slug", "").strip()
        content = request.POST.get("content", "").strip()

        if title and slug and content:
            Post.objects.create(
                author=request.user if request.user.is_authenticated else User.objects.first(),
                title=title,
                slug=slug,
                content=content,
            )
            return redirect("hub:post_detail", slug=slug)

    return render(request, "hub/post_form.html")