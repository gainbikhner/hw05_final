from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class UserViewsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='TestUser')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('users:signup'): 'users/signup.html',
            reverse('users:login'): 'users/login.html',
            reverse('users:password_change_done'): (
                'users/password_change_done.html'
            ),
            reverse('users:password_change'): (
                'users/password_change_form.html'
            ),
            reverse('users:password_reset_done'): (
                'users/password_reset_done.html'
            ),
            reverse('users:password_reset'): 'users/password_reset_form.html',
            reverse('users:password_reset_complete'): (
                'users/password_reset_complete.html'
            ),
            reverse(
                'users:password_reset_confirm',
                kwargs={
                    'uidb64': 'Mw',
                    'token': '67g-e71c1698a60606b06e1c'
                }
            ): 'users/password_reset_confirm.html',
            reverse('users:logout'): 'users/logged_out.html'
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_signup_show_correct_context(self):
        """Шаблон signup сформирован с правильным контекстом."""
        form_fields = {
            'first_name': forms.fields.CharField,
            'last_name': forms.fields.CharField,
            'username': forms.fields.CharField,
            'email': forms.fields.EmailField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                response = self.authorized_client.get(reverse('users:signup'))
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
