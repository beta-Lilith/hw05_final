from django.test import TestCase, Client
from posts.models import Post, Group, User
from django.urls import reverse
from http import HTTPStatus
from django.core.cache import cache


class PostURLTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='Василий')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Много текста тестового поста',
            author=cls.user,
        )
        cls.templates_urls = {
            reverse('posts:index'):
                'posts/index.html',
            reverse('posts:group_list', args=[cls.group.slug]):
                'posts/group_list.html',
            reverse('posts:profile', args=[cls.post.author]):
                'posts/profile.html',
            reverse('posts:post_detail', args=[cls.post.id]):
                'posts/post_detail.html',
            reverse('posts:post_create'):
                'posts/post_create.html',
            reverse('posts:post_edit', args=[cls.post.id]):
                'posts/post_create.html',
        }

    def setUp(self):

        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""

        for url, template in PostURLTests.templates_urls.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_response_for_authorized(self):
        """Автору доступны все страницы и редактирование своих постов."""

        for url in PostURLTests.templates_urls.keys():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_response_for_guest(self):
        """Проверка доступов для неавторизованного пользователя."""

        allowed_urls = [
            reverse('posts:index'),
            reverse('posts:group_list', args=[PostURLTests.group.slug]),
            reverse('posts:profile', args=[PostURLTests.post.author]),
            reverse('posts:post_detail', args=[PostURLTests.post.id]),
        ]
        for url in allowed_urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

        redirect_urls = {
            reverse('posts:post_create'):
                '/auth/login/?next=/create/',
            reverse('posts:post_edit', args=[PostURLTests.post.id]):
                f'/auth/login/?next=/posts/{PostURLTests.post.id}/edit/',
            reverse('posts:add_comment', args=[PostURLTests.post.id]):
                f'/auth/login/?next=/posts/{PostURLTests.post.id}/comment/',
        }
        for url, redirect in redirect_urls.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(response, redirect)

    def test_post_edit_only_author(self):
        """Авторизованный пользователь не может редактировать чужой пост."""

        self.user = User.objects.create_user(username='Засланец')
        self.authorized_client.force_login(self.user)

        response = self.authorized_client.get(
            reverse(
                'posts:post_edit', args=[PostURLTests.post.id]), follow=True
        )
        redirect = reverse('posts:post_detail', args=[PostURLTests.post.id])
        self.assertRedirects(response, redirect)

    def test_404(self):
        """Проверка несуществующей страницы."""

        # Correct status code
        response = self.guest_client.get("/oops/")
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        response = self.authorized_client.get("/oops/")
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        # Correct template
        response = self.guest_client.get('/oops/')
        self.assertTemplateUsed(response, 'core/404.html')
        response = self.authorized_client.get('/oops/')
        self.assertTemplateUsed(response, 'core/404.html')
