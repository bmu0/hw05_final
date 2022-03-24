from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required

from yatube.settings import POSTS_PAGE_COUNT
from .models import Post, Group, Follow
from .forms import PostForm, PostEditForm, CommentForm

User = get_user_model()


def index(request):
    template = 'posts/index.html'
    post_list = Post.objects.all()
    paginator = Paginator(post_list, POSTS_PAGE_COUNT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'title': 'Последние обновления на сайте'
    }
    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.group_name.all()
    paginator = Paginator(post_list, POSTS_PAGE_COUNT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
        'title': f'Записи сообщества {group}'
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    following = False
    post_list = Post.objects.filter(author__username=username)
    paginator = Paginator(post_list, POSTS_PAGE_COUNT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    author = get_object_or_404(User, username=username)
    if request.user.is_authenticated:
        subscribes = Follow.objects.filter(user=request.user)
        for i in subscribes:
            if i.author == author:
                following = True
    subscribers = len(Follow.objects.filter(author__username=username))
    context = {
        'subscribers': subscribers,
        'following': following,
        'title': f'Профайл пользователя {username}',
        'page_obj': page_obj,
        'author': author,
        'post_list': post_list,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    post_list = Post.objects.filter(author__username=post.author.username)
    form = CommentForm(request.POST or None)
    context = {
        'title': post,
        'post': post,
        'post_list': post_list,
        'form': form,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None,)
    if form.is_valid():
        text = form.cleaned_data['text']
        group = form.cleaned_data['group']
        image = form.cleaned_data['image']
        user = request.user
        Post.objects.create(
            text=text,
            group=group,
            author=user,
            image=image
        )
        return redirect('posts:profile', request.user)
    else:
        form = PostForm()
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    is_edit = True
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect(f'/posts/{post_id}/')
    if request.method == 'POST':
        form = PostEditForm(
            request.POST or None,
            files=request.FILES or None,
            instance=post
        )
        if form.is_valid():
            form.save()
            return redirect(f'/posts/{post_id}/')
    else:
        form = PostEditForm(instance=post)
    context = {'form': form, 'is_edit': is_edit, }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    post = Post.objects.get(id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    template = 'posts/follow.html'
    # post_list = Post.objects.all()
    subscribes = []
    subscribes_query = Follow.objects.filter(user=request.user)
    for i in subscribes_query:
        subscribes.append(i.author.username)
    post_list = Post.objects.filter(author__username__in=subscribes)
    print(subscribes)
    paginator = Paginator(post_list, POSTS_PAGE_COUNT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'title': 'Мои подписки'
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    if username != request.user.username:
        subscribes = []
        subscribes_query = Follow.objects.filter(user=request.user)
        for i in subscribes_query:
            subscribes.append(i.author.username)
        if username not in subscribes:
            Follow.objects.create(
                user=request.user,
                author=User.objects.get(username=username)
            )
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    Follow.objects.get(
        user=request.user,
        author=User.objects.get(username=username)
    ).delete()
    return redirect('posts:profile', username)
