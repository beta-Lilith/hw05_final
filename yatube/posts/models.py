from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Group(models.Model):
    """Модель групп."""

    def __str__(self):
        return self.title

    title = models.CharField(
        max_length=200,
        verbose_name='имя группы',
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name='URL',
    )
    description = models.TextField(
        verbose_name='описание группы',
    )

    class Meta:
        verbose_name = 'группа'
        verbose_name_plural = 'группы'


class Post(models.Model):
    """Модель постов."""

    def __str__(self):
        return self.text[:15]

    text = models.TextField(
        verbose_name='текс поста',
        help_text='Поле обязательно для заполнения, не оставляйте его пустым.',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='дата создания',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='автор'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        related_name='posts',
        blank=True,
        null=True,
        verbose_name='группа',
        help_text='У вашего поста есть группа?',
    )
    image = models.ImageField(
        verbose_name='картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        verbose_name = 'пост'
        verbose_name_plural = 'посты'
        ordering = ['-pub_date']


class Comment(models.Model):
    """Модель комментариев."""

    def __str__(self):
        return self.text[:15]

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='пост',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='автор'
    )
    text = models.TextField(
        verbose_name='текс комментария',
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='дата создания',
    )

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'комментарии'
        ordering = ['-created']


class Follow(models.Model):
    """Модель подписчиков."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        related_name='follower',
        verbose_name='подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='автор'
    )

    class Meta:
        verbose_name = 'подписчик'
        verbose_name_plural = 'подписчики'
