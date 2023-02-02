from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class UserURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='TestUser')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_for_anonymous_exists_at_desired_location(self):
        """Страницы для неавторизованных доступны любому пользователю."""
        urls_for_anonymous = [
            '/auth/signup/',
            '/auth/logout/',
            '/auth/login/',
            '/auth/password_reset/done/',
            '/auth/password_reset/',
            '/auth/reset/done/',
            '/auth/reset/Mw/673-218ce6562ab6af78e8f9/'
        ]
        for url in urls_for_anonymous:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_for_authorized_user_exists_at_desired_location(self):
        """Страницы доступны авторизованному пользователю."""
        urls_for_authorized_user = [
            '/auth/password_change/done/',
            '/auth/password_change/'
        ]
        for url in urls_for_authorized_user:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_redirect_anonymous_on_admin_login(self):
        """Страницы перенаправят анонимного пользователя на страницу логина."""
        urls_for_authorized_user = [
            '/auth/password_change/done/',
            '/auth/password_change/'
        ]
        for url in urls_for_authorized_user:
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                redirect_link = f'/auth/login/?next={url}'
                self.assertRedirects(response, redirect_link)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/auth/signup/': 'users/signup.html',
            '/auth/login/': 'users/login.html',
            '/auth/password_reset/done/': 'users/password_reset_done.html',
            '/auth/password_reset/': 'users/password_reset_form.html',
            '/auth/reset/done/': 'users/password_reset_complete.html',
            '/auth/reset/Mw/673-218ce6562ab6af78e8f9/': (
                'users/password_reset_confirm.html'
            ),
            '/auth/password_change/done/': 'users/password_change_done.html',
            '/auth/password_change/': 'users/password_change_form.html',
            '/auth/logout/': 'users/logged_out.html'
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
