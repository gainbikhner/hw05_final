from http import HTTPStatus

from django.test import Client, TestCase


class AboutURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_urls_exists_at_desired_location(self):
        """Страницы доступны любому пользователю."""
        urls = [
            '/about/author/',
            '/about/tech/'
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html'
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)
