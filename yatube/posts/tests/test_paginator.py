from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()

NUMBER_OF_POSTS = 11
POSTS_ON_PAGE = 10
EXTRA_POSTS = 1


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )
        posts_list = []
        for i in range(NUMBER_OF_POSTS):
            post = Post(
                author=cls.user,
                text='Тестовый пост',
                group=cls.group
            )
            posts_list.append(post)
        Post.objects.bulk_create(posts_list)

    def setUp(self):
        self.guest_client = Client()

    def test_one_page_contains_ten_records(self):
        """Количество постов на странице равно 10."""
        pages_names = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}),
            reverse('posts:profile', kwargs={'username': 'auth'})
        ]
        for name in pages_names:
            with self.subTest(name=name):
                first_page_response = self.guest_client.get(name)
                second_page_response = self.guest_client.get(name + '?page=2')
                self.assertEqual(
                    len(first_page_response.context['page_obj']),
                    POSTS_ON_PAGE
                )
                self.assertEqual(
                    len(second_page_response.context['page_obj']),
                    EXTRA_POSTS
                )
