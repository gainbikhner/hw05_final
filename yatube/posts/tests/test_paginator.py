from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Follow, Group, Post

User = get_user_model()

NUMBER_OF_POSTS = 11
POSTS_ON_PAGE = 10
EXTRA_POSTS = 1


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )
        posts_list = []
        for i in range(NUMBER_OF_POSTS):
            post = Post(
                author=cls.author,
                text='Тестовый пост',
                group=cls.group
            )
            posts_list.append(post)
        Post.objects.bulk_create(posts_list)
        cls.user = User.objects.create_user(username='user')
        cls.follow = Follow.objects.create(
            user=cls.user,
            author=cls.author
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PaginatorViewsTest.user)

    def test_one_page_contains_ten_records(self):
        """Количество постов на странице равно 10."""
        pages_names = [
            reverse('posts:index'),
            reverse(
                'posts:group_list',
                kwargs={'slug': PaginatorViewsTest.group.slug}
            ),
            reverse(
                'posts:profile',
                kwargs={'username': PaginatorViewsTest.author}
            ),
            reverse('posts:follow_index')
        ]
        for name in pages_names:
            with self.subTest(name=name):
                first_page_response = self.authorized_client.get(name)
                second_page_response = self.authorized_client.get(
                    name + '?page=2'
                )
                self.assertEqual(
                    len(first_page_response.context['page_obj']),
                    POSTS_ON_PAGE
                )
                self.assertEqual(
                    len(second_page_response.context['page_obj']),
                    EXTRA_POSTS
                )
