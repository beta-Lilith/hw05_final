from django.test import TestCase, Client
from django.urls import reverse
from django import forms
from posts.models import Post, Group, User, Follow
from django.core.cache import cache
import time


class PostPagesTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='Василий')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        # Post without a group
        cls.post_1 = Post.objects.create(
            text='Много текста тестового поста',
            author=cls.user,
        )

    def setUp(self):

        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        # Post with the group
        self.post_2 = Post.objects.create(
            text='С группой очень много текста тестового поста',
            author=self.user,
            group=self.group,
        )

    def test_index_context(self):
        """Шаблон index использует правильный контекст."""

        response = self.guest_client.get(reverse('posts:index'))
        # Headline
        self.assertEqual(
            response.context['headline'], 'Последние обновления на сайте')
        # Proper object and correct order DESC
        self.assertEqual(
            response.context['page_obj'][0], self.post_2)
        # Objects list
        self.assertEqual(
            len(response.context['page_obj']), 2)

    def test_index_cache(self):
        """Посты index кэшируются на 20 секунд."""

        response = self.guest_client.get(reverse('posts:index'))
        page_0 = response.content
        Post.objects.create(
            text='Новый умный пост',
            author=PostPagesTests.user,
        )
        # Content didn't change
        response_2 = self.guest_client.get(reverse('posts:index'))
        page_1 = response_2.content
        self.assertEqual(page_0, page_1)
        # Content changed after 20 seconds
        time.sleep(20)
        response_2 = self.guest_client.get(reverse('posts:index'))
        page_2 = response_2.content
        self.assertNotEqual(page_0, page_2)

    def test_group_list_context(self):
        """Шаблон group_list использует правильный контекст."""

        response = self.guest_client.get(
            reverse('posts:group_list', args=[PostPagesTests.group.slug]))

        # Headline
        self.assertEqual(
            response.context['headline'], 'Записи сообщества: ')
        # Group
        self.assertEqual(
            response.context['group'], PostPagesTests.group)
        # Proper object
        self.assertEqual(
            response.context['page_obj'][0], self.post_2)
        # Objects list
        self.assertEqual(
            len(response.context['page_obj']), 1)

    def test_profile_context(self):
        """Шаблон profile использует правильный контекст."""

        response = self.guest_client.get(
            reverse('posts:profile', args=[PostPagesTests.post_1.author]))

        # Headline
        self.assertEqual(
            response.context['headline'], 'Все посты пользователя ')
        # Username
        self.assertEqual(
            response.context['username'], PostPagesTests.user)
        # Number of posts created by author
        self.assertEqual(
            response.context['n_posts'], 2)
        # Proper object
        self.assertEqual(
            response.context['page_obj'][0], self.post_2)
        # Objects list
        self.assertEqual(
            len(response.context['page_obj']), 2)

    def test_post_detail_context(self):
        """Шаблон post_detail использует правильный контекст."""

        response = self.guest_client.get(
            reverse('posts:post_detail', args=[PostPagesTests.post_1.id]))

        # Headline
        self.assertEqual(
            response.context['headline'], 'Вся информация о посте')
        # Post
        self.assertEqual(
            response.context['post'], PostPagesTests.post_1)
        # Number of posts created by author
        self.assertEqual(
            response.context['n_posts'], 2)

    def test_post_create_context(self):
        """Шаблон post_create(create) использует правильный контекст."""

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ChoiceField,
            'image': forms.fields.ImageField,
        }
        response = self.authorized_client.get(
            reverse('posts:post_create'))

        # Form create
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_context(self):
        """Шаблон post_create(edit) использует правильный контекст."""

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ChoiceField,
            'image': forms.fields.ImageField,
        }
        response = self.authorized_client.get(
            reverse('posts:post_edit', args=[PostPagesTests.post_1.id]))

        # Form edit
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        # Post for edit
        self.assertEqual(
            response.context['post'], PostPagesTests.post_1)
        # is_edit
        self.assertEqual(
            response.context['is_edit'], True)

    def test_can_follow_unfollow(self):
        """Авторизованный пользователь может подписываться/отписываться."""

        mister_x = User.objects.create_user(username='Подписчег')
        self.authorized_client.force_login(mister_x)
        url = reverse('posts:follow_index')

        # Doesn't have following posts
        response = self.authorized_client.get(url)
        following_posts = len(response.context['page_obj'])
        self.assertEqual(following_posts, 0)

        # Can Follow
        Follow.objects.get_or_create(
            user=mister_x,
            author=PostPagesTests.user,
        )
        response = self.authorized_client.get(url)
        following_posts = len(response.context['page_obj'])
        self.assertEqual(following_posts, 2)

        # Another user doesn't have following posts
        self.authorized_client.force_login(PostPagesTests.user)
        response = self.authorized_client.get(url)
        following_posts = len(response.context['page_obj'])
        self.assertEqual(following_posts, 0)

        # Can unfollow
        self.authorized_client.force_login(mister_x)
        Follow.objects.all().delete()
        response = self.authorized_client.get(url)
        following_posts = len(response.context['page_obj'])
        self.assertEqual(following_posts, 0)

    # Комментарий ревьюеру:
    # Теперь не уверена, что нужны эти 2 теста, потому что
    # я вместо задания 6 спринта просто проверить контекст сделала пошире
    # проверки в test_forms, что посты после добавления
    # появляются на нужных страницах..

    def test_new_post_with_group_on_right_page(self):
        """Новый пост с группой появится на index, group_list, profile."""

        urls = [
            reverse('posts:index'),
            reverse('posts:group_list', args=[PostPagesTests.group.slug]),
            reverse('posts:profile', args=[self.post_2.author]),
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                expected = Post.objects.filter(group=self.post_2.group).last()
                self.assertEqual(response.context['page_obj'][0], expected)

    def test_new_post_not_in_wrong_group(self):
        """Новый пост с группой не появится в чужой группе."""

        response = self.guest_client.get(
            reverse('posts:group_list', args=[PostPagesTests.group.slug]))

        not_expected = Post.objects.exclude(group=self.post_2.group)
        self.assertNotIn(
            not_expected, response.context['page_obj'].object_list)
