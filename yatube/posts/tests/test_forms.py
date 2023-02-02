import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            group=cls.group,
            author=cls.user
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='TestUser')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author_client = Client()
        self.author_client.force_login(PostFormTests.user)

    def test_post_create(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст 2',
            'group': self.group.id
        }
        response = self.author_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': 'auth'})
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                group=form_data['group'],
                author=self.post.author
            ).exists()
        )

    def test_post_create_withot_group(self):
        """Валидная форма создает запись в Post без указания группы."""
        posts_count = Post.objects.count()
        form_data = {'text': 'Тестовый текст 2'}
        response = self.author_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': 'auth'})
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                author=self.post.author,
                group=None
            ).exists()
        )

    def test_post_edit(self):
        """Валидная форма редактирует запись в Post."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Отредактированный текст',
            'group': self.group.id
        }
        response = self.author_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(
            Post.objects.filter(
                id=self.post.id,
                text=form_data['text'],
                group=form_data['group'],
                author=self.post.author,
                pub_date=self.post.pub_date
            ).exists()
        )

    def test_post_create_for_guest_client(self):
        """При POST-запросе не будет создаваться новый пост
        для неавторизованного пользователя.
        """
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст 2',
            'group': self.group.id
        }
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        redirect_link = '/auth/login/?next=/create/'
        self.assertRedirects(response, redirect_link)
        self.assertEqual(Post.objects.count(), posts_count)

    def test_post_edit_for_guest_client(self):
        """При POST-запросе неавторизованного пользователя
        пост не будет отредактирован.
        """
        form_data = {
            'text': 'Отредактированный текст',
            'group': self.group.id
        }
        response = self.guest_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        redirect_link = '/auth/login/?next=/posts/1/edit/'
        self.assertRedirects(response, redirect_link)
        self.assertTrue(
            Post.objects.filter(
                id=self.post.id,
                text=self.post.text,
                group=self.post.group,
                author=self.post.author,
                pub_date=self.post.pub_date
            ).exists()
        )

    def test_post_edit_for_authorized_client(self):
        """При POST-запросе неавтора пост не будет отредактирован."""
        form_data = {
            'text': 'Отредактированный текст',
            'group': self.group.id
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        self.assertTrue(
            Post.objects.filter(
                id=self.post.id,
                text=self.post.text,
                group=self.post.group,
                author=self.post.author,
                pub_date=self.post.pub_date
            ).exists()
        )

    def test_post_create_with_image(self):
        """Валидная форма с картинкой создает запись в Post."""
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
            'text': 'Тестовый текст 2',
            'group': self.group.id,
            'image': uploaded
        }
        response = self.author_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': 'auth'})
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                group=form_data['group'],
                author=self.post.author,
                image='posts/small.gif'
            ).exists()
        )

    def test_add_comment_for_authorized_client(self):
        """Авторизованный пользователь может комментировать посты."""
        comments_count = self.post.comments.count()
        form_data = {'text': 'Тестовый комментарий'}
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk})
        )
        self.assertEqual(self.post.comments.count(), comments_count + 1)
        self.assertTrue(
            self.post.comments.filter(text=form_data['text']).exists()
        )

    def test_add_comment_for_guest_client(self):
        """Неавторизованный пользователь не может комментировать посты."""
        comments_count = self.post.comments.count()
        form_data = {'text': 'Тестовый комментарий'}
        response = self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )
        redirect_link = '/auth/login/?next=/posts/1/comment/'
        self.assertRedirects(response, redirect_link)
        self.assertEqual(self.post.comments.count(), comments_count)
