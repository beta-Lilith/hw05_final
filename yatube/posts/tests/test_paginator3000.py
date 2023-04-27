from django.test import TestCase, Client
from django.urls import reverse
from posts.models import Post, Group, User
from posts.views import POSTS_PER_PAGE


ADDITIONAL_PAGES = 4
TOTAL_PAGES = POSTS_PER_PAGE + ADDITIONAL_PAGES


class Paginator3000Test(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create(username='Василий3000')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        for i in range(TOTAL_PAGES):
            Post.objects.create(
                text=f'Пост паджинатору {i}',
                author=cls.user,
                group=cls.group
            )

    def setUp(self):

        self.guest_client = Client()

    def test_paginator(self):
        """Правильное отображение количества страниц паджинатором."""

        urls = [
            reverse('posts:index'),
            reverse('posts:group_list', args=[Paginator3000Test.group.slug]),
            reverse('posts:profile', args=[Paginator3000Test.user]),
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(
                    len(response.context.get('page_obj')), POSTS_PER_PAGE)
                response = self.guest_client.get(url + '?page=2')
                self.assertEqual(
                    len(response.context.get('page_obj')), ADDITIONAL_PAGES)
