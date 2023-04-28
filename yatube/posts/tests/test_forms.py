import shutil
import tempfile
from posts.models import Post, Group, User, Comment
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from http import HTTPStatus
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='Василий')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.group_change = Group.objects.create(
            title='Другая группа',
            slug='test_slug_2',
            description='Другое тестовое описание'
        )
        cls.post = Post.objects.create(
            text='Много текста тестового поста',
            author=cls.user,
            group=cls.group,
        )
        cls.urls = [
            reverse('posts:index'),
            reverse('posts:profile', args=[cls.user]),
            reverse('posts:group_list', args=[cls.group.slug]),
        ]

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):

        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""

        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовый текст',
            'group': PostFormTests.group.id,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, reverse('posts:profile', args=[PostFormTests.user]))
        self.assertEqual(Post.objects.count(), posts_count + 1)

        # Index, profile, group_list
        for url in PostFormTests.urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url).context['page_obj']
                self.assertIn(
                    Post.objects.get(
                        text=form_data['text'],
                        author=PostFormTests.user,
                        group=form_data['group'],
                        image='posts/small.gif'
                    ), response
                )
        # Post_detail
        post = Post.objects.first()
        url = reverse(
            'posts:post_detail', args=[post.id])
        response = self.authorized_client.get(url).context['post']
        self.assertEqual(
            Post.objects.get(
                text=form_data['text'],
                author=PostFormTests.user,
                group=form_data['group'],
                image='posts/small.gif'
            ), response
        )
        # Post exists in DATABASE
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                author=PostFormTests.post.author,
                group=form_data['group'],
                image='posts/small.gif'
            ).exists()
        )

    def test_edit_post(self):
        """Валидная форма редактирует запись, группу и картинку в Post."""

        posts_count = Post.objects.count()
        big_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded_2 = SimpleUploadedFile(
            name='big.gif',
            content=big_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Измененный тестовый текст',
            'group': PostFormTests.group_change.id,
            'image': uploaded_2,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', args=[PostFormTests.post.id]),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', args=[PostFormTests.post.id]))
        self.assertEqual(Post.objects.count(), posts_count)

        # Edited post on index, profile:
        for url in PostFormTests.urls[0:2]:
            with self.subTest(url=url):
                response = self.authorized_client.get(url).context['page_obj']
                self.assertIn(
                    Post.objects.get(
                        text=form_data['text'],
                        author=PostFormTests.user,
                        group=form_data['group'],
                        image='posts/big.gif'
                    ), response
                )
        # Edited post on correct group_list
        url = reverse(
            'posts:group_list', args=[PostFormTests.group_change.slug])
        response = self.authorized_client.get(url).context['page_obj']
        self.assertIn(
            Post.objects.get(
                text=form_data['text'],
                author=PostFormTests.user,
                group=form_data['group'],
                image='posts/big.gif'
            ), response
        )
        # Post_detail
        url = reverse(
            'posts:post_detail', args=[self.post.id])
        response = self.authorized_client.get(url).context['post']
        self.assertEqual(
            Post.objects.get(
                text=form_data['text'],
                author=PostFormTests.user,
                group=form_data['group'],
                image='posts/big.gif'
            ), response
        )
        # Post with initial group doesn't exist in DATABASE
        self.assertFalse(
            Post.objects.filter(
                text=form_data['text'],
                author=PostFormTests.post.author,
                group=PostFormTests.group.id,
                image='posts/big.gif'
            ).exists()
        )

    def test_cant_create_empty_post(self):
        """Нельзя создать пустой пост, сайт не падает."""

        posts_count = Post.objects.count()
        form_data = {
            'text': '',
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertFormError(
            response,
            'form',
            'text',
            'Обязательное поле.',
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)


class CommentFormTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='Василий троль')
        cls.author = User.objects.create_user(username='Толстой')
        cls.post = Post.objects.create(
            text='Много текста тестового поста',
            author=cls.author,
        )

    def setUp(self):

        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_comment_form(self):
        """После успешной отправки комментарий появляется на странице поста."""

        comments_count = CommentFormTests.post.comments.count()
        form_data = {
            'text': 'Гневный комментарий',
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', args=[CommentFormTests.post.id]),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', args=[CommentFormTests.post.id]))
        self.assertEqual(
            CommentFormTests.post.comments.count(), comments_count + 1)
        self.assertTrue(
            Comment.objects.filter(
                text=form_data['text'],
                author=CommentFormTests.user,
            ).exists()
        )
