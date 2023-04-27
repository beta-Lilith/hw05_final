from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from .models import Post, Group, User, Follow
from .forms import PostForm, CommentForm
from django.shortcuts import redirect
# from django.views.decorators.cache import cache_page

POSTS_PER_PAGE = 10


# Паджинатор
def paginator_3000(post_list, request):

    paginator = Paginator(post_list, POSTS_PER_PAGE)
    # Из URL извлекаем номер запрошенной страницы - это значение параметра page
    page_number = request.GET.get('page')
    # Получаем набор записей для страницы с запрошенным номером
    page_obj = paginator.get_page(page_number)

    return page_obj


# Главная страница
# @cache_page(20, key_prefix="index_page")
def index(request):

    template = 'posts/index.html'
    headline = 'Последние обновления на сайте'

    post_list = Post.objects.all()

    context = {
        'headline': headline,
        'page_obj': paginator_3000(post_list, request),
    }
    return render(request, template, context)


# Страница постов, отфильтрованных по группам
def group_posts(request, slug):

    # Функция get_object_or_404 получает по заданным критериям объект
    # из базы данных или возвращает сообщение об ошибке, если объект не найден.
    # В нашем случае в переменную group будут переданы объекты модели Group,
    # поле slug у которых соответствует значению slug в запросе
    group = get_object_or_404(Group, slug=slug)
    template = 'posts/group_list.html'
    headline = 'Записи сообщества: '

    post_list = group.posts.all()

    context = {
        'headline': headline,
        'group': group,
        'page_obj': paginator_3000(post_list, request),
    }
    return render(request, template, context)


# Страница пользователя/автора
def profile(request, username):

    username = get_object_or_404(User, username=username)
    template = 'posts/profile.html'
    headline = f'Все посты пользователя {username.get_full_name()}'

    n_posts = username.posts.count()
    post_list = username.posts.all()
    following = username.following.exists()

    context = {
        'headline': headline,
        'username': username,
        'n_posts': n_posts,
        'following': following,
        'page_obj': paginator_3000(post_list, request),
    }
    return render(request, template, context)


# Подробная инфа о посте
def post_detail(request, post_id):

    post = get_object_or_404(Post, id=post_id)
    template = 'posts/post_detail.html'
    headline = 'Вся информация о посте'

    comments = post.comments.select_related('post')
    form = CommentForm(request.POST or None)
    n_posts = post.author.posts.count()

    context = {
        'headline': headline,
        'post': post,
        'n_posts': n_posts,
        'form': form,
        'comments': comments,
        'is_edit': True,
    }
    return render(request, template, context)


# Страница создания нового поста
@login_required
def post_create(request):

    template = 'posts/post_create.html'

    form = PostForm(
        request.POST or None,
        # 6Sprint
        files=request.FILES or None
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=request.user)

    context = {
        'form': form,
    }
    return render(request, template, context)


# Страница редактирования поста (только автор)
@login_required
def post_edit(request, post_id):

    post = get_object_or_404(Post, id=post_id)
    template = 'posts/post_create.html'

    if request.user != post.author:
        return redirect('posts:post_detail', post_id)
    form = PostForm(
        request.POST or None,
        # 6Sprint
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:post_detail', post_id=post_id)

    context = {
        'form': form,
        'post': post,
        'is_edit': True,
    }
    return render(request, template, context)


# Страница добавления комментария к посту на странице поста
@login_required
def add_comment(request, post_id):

    post = get_object_or_404(Post, id=post_id)

    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()

    return redirect('posts:post_detail', post_id=post_id)


# Страница постов авторов, на которых подписан текущий пользователь.
@login_required
def follow_index(request):

    post_list = Post.objects.filter(author__following__user=request.user)
    template = 'posts/follow.html'
    headline = 'Ваши подписки'

    context = {
        'headline': headline,
        'page_obj': paginator_3000(post_list, request),
    }
    return render(request, template, context)


# Подписаться на автора
@login_required
def profile_follow(request, username):

    author = get_object_or_404(User, username=username)

    if author != request.user:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:profile', author)


# Дизлайк, отписка
@login_required
def profile_unfollow(request, username):

    author = get_object_or_404(User, username=username)

    if author != request.user:
        Follow.objects.filter(user=request.user, author=author).delete()
    return redirect('posts:profile', author)
