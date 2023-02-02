from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(author=cls.user, text='Тестовый пост')

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='TestUser')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author_client = Client()
        self.author_client.force_login(PostURLTests.user)

    def test_urls_for_anonymous_exists_at_desired_location(self):
        """Страницы для неавторизованных доступны любому пользователю."""
        urls_for_anonymous = [
            '/',
            '/group/test-slug/',
            '/profile/TestUser/',
            '/posts/1/'
        ]
        for url in urls_for_anonymous:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_create_url_exists_at_desired_location(self):
        """Страница /create/ доступна авторизованному пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_exists_at_desired_location(self):
        """Страница /posts/1/edit/ доступна автору поста."""
        response = self.author_client.get('/posts/1/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unexisting_page_url_exists_at_404(self):
        """Запрос к /unexisting_page/ вернёт ошибку 404."""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_post_create_url_redirect_anonymous_on_admin_login(self):
        """Страница /create/ перенаправит анонимного пользователя
        на страницу логина.
        """
        response = self.guest_client.get('/create/', follow=True)
        redirect_link = '/auth/login/?next=/create/'
        self.assertRedirects(response, redirect_link)

    def test_post_edit_url_redirect_anonymous_on_post_detail(self):
        """Страница /posts/1/edit/ перенаправит анонимного пользователя
        на страницу логина.
        """
        response = self.guest_client.get('/posts/1/edit/', follow=True)
        redirect_link = '/auth/login/?next=/posts/1/edit/'
        self.assertRedirects(response, redirect_link)

    def test_post_edit_url_redirect_no_author_on_post_detail(self):
        """Страница /posts/1/edit/ перенаправит неавтора на страницу поста."""
        response = self.authorized_client.get('/posts/1/edit/', follow=True)
        redirect_link = '/posts/1/'
        self.assertRedirects(response, redirect_link)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/TestUser/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
            '/posts/1/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html'
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertTemplateUsed(response, template)
