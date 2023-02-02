from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')

    def setUp(self):
        self.guest_client = Client()

    def test_signup(self):
        """Валидная форма создает запись в User."""
        users_count = User.objects.count()
        form_data = {
            'first_name': 'Иван',
            'last_name': 'Иванов',
            'username': 'ivanov',
            'email': 'ivanov@gmail.com',
            'password1': 'parolparol',
            'password2': 'parolparol'
        }
        response = self.guest_client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:index'))
        self.assertEqual(User.objects.count(), users_count + 1)
        self.assertTrue(User.objects.filter(
            first_name='Иван',
            last_name='Иванов',
            username='ivanov',
            email='ivanov@gmail.com'
        ).exists())
