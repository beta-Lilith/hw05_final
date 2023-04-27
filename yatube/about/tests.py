from django.test import TestCase, Client
from django.urls import reverse
from http import HTTPStatus


class AboutTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.templates = {
            reverse('about:author'):
                'about/author.html',
            reverse('about:tech'):
                'about/tech.html',
        }

    def setUp(self):
        self.guest_client = Client()

    def test_url_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""

        for url, template in AboutTests.templates.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_response(self):
        """Доступны все страницы about."""

        for url in AboutTests.templates.keys():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
