from django.test import Client, TestCase


class URLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_404_page_uses_correct_template(self):
        """Страница 404 использует кастомный шаблон."""
        response = self.guest_client.get('/error/')
        template = 'core/404.html'
        self.assertTemplateUsed(response, template)
