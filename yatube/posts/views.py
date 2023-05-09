from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import cache_page

from .models import Follow, Post, Group, User
from .forms import CommentForm, PostForm


NUMB_OF_POSTS = 10


def get_page_object(request, post_list):
    paginator = Paginator(post_list, NUMB_OF_POSTS)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


@cache_page(20, key_prefix="index_page")
def index(request):
    post_list = Post.objects.all()
    context = {
        'page_obj': get_page_object(request, post_list),
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.select_related('group')
    context = {
        'group': group,
        'page_obj': get_page_object(request, post_list),
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    # post_list = group.posts.select_related('group')
    if author.following:
        following = True
    else:
        following = False
    context = {
        'author': author,
        'page_obj': get_page_object(request, post_list),
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    posts = Post.objects.all()
    form = CommentForm(request.POST or None)
    comments = post.comments.all()
    context = {
        'post': post,
        'posts': posts,
        'form': form,
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
@csrf_exempt
def post_create(request):
    form = PostForm(request.POST or None,
                    files=request.FILES or None
                    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', request.user.username)
    context = {
        'form': form,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
@csrf_exempt
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        post.save()
        return redirect('posts:post_detail', post_id=post_id)
    context = {
        'post': post,
        'form': form,
        'is_edit': True,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
@csrf_exempt
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
@csrf_exempt
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    context = {
        'page_obj': get_page_object(request, post_list),
    }
    return render(request, 'posts/follow.html', context)


@login_required
@csrf_exempt
def profile_follow(request, username):
    # Подписаться на автора
    author = get_object_or_404(User, username=username)
    if request.user.username != username:
        Follow.objects.get_or_create(
            user=request.user,
            author=author)
    return redirect('posts:profile', username=username)


@login_required
@csrf_exempt
def profile_unfollow(request, username):
    # Отписка
    author = get_object_or_404(User, username=username)
    Follow.objects.get(
        user=request.user,
        author=author
    ).delete()
    return redirect('posts:profile', author.username)
