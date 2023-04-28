from django.test import TestCase
from posts.models import Post, Group, User


class PostModelTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='Василий')
        cls.post = Post.objects.create(
            text='Много текста тестового поста',
            author=cls.user,
        )

    def test_have_correct_str(self):
        """__str__ Post совпадает с ожидаемым."""

        post = PostModelTest.post
        expected_object_name = post.text[:15]
        self.assertEqual(expected_object_name, str(post))

    def test_verbose_name(self):
        """verbose_name Post в полях совпадает с ожидаемым."""

        post = PostModelTest.post
        field_verboses = {
            'text': 'текс поста',
            'pub_date': 'дата создания',
            'author': 'автор',
            'group': 'группа',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value)

    def test_help_text(self):
        """help_text Post в полях совпадает с ожидаемым."""

        post = PostModelTest.post
        field_help_texts = {
            'text': ('Поле обязательно для заполнения, '
                     'не оставляйте его пустым.'),
            'group': 'У вашего поста есть группа?',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value)


class GroupModelTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )

    def test_have_correct_str(self):
        """__str__ Group совпадает с ожидаемым."""

        group = GroupModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))

    def test_verbose_name(self):
        """verbose_name Group в полях совпадает с ожидаемым."""

        group = GroupModelTest.group
        field_verboses = {
            'title': 'имя группы',
            'slug': 'URL',
            'description': 'описание группы',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).verbose_name, expected_value)
