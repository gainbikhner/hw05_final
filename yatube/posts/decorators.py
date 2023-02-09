from django.shortcuts import get_object_or_404, redirect

from .models import Post


def author_only(func):
    def wrapper(request, post_id, *args, **kwargs):
        post = get_object_or_404(Post, id=post_id)
        if request.user == post.author:
            return func(request, post_id, *args, **kwargs)
        return redirect('posts:post_detail', post_id)
    return wrapper
