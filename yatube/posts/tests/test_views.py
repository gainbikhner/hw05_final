import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Follow, Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.image = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
            image=cls.image
        )
        cls.another_group = Group.objects.create(
            title='Другая тестовая группа',
            slug='test-slug-2',
            description='Тестовое описание'
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Тестовый комментарий'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.user = User.objects.create_user(username='TestUser')
        self.another_user = User.objects.create_user(username='AnotherUser')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author_client = Client()
        self.author_client.force_login(PostViewsTests.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}): (
                'posts/group_list.html'
            ),
            reverse('posts:profile', kwargs={'username': 'auth'}): (
                'posts/profile.html'
            ),
            reverse('posts:post_detail', kwargs={'post_id': 1}): (
                'posts/post_detail.html'
            ),
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit', kwargs={'post_id': 1}): (
                'posts/create_post.html'
            )
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.author_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_pages_show_correct_context_page_obj(self):
        """Шаблоны сформированы с правильным контекстом page_obj."""
        pages_names = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}),
            reverse('posts:profile', kwargs={'username': 'auth'})
        ]
        for name in pages_names:
            with self.subTest(name=name):
                response = self.author_client.get(name)
                page_object = response.context['page_obj'][0]
                self.assertEqual(page_object.text, PostViewsTests.post.text)
                self.assertEqual(page_object.author, PostViewsTests.user)
                self.assertEqual(page_object.group, PostViewsTests.group)

    def test_group_list_page_shows_correct_context_group(self):
        """Шаблон group_list сформирован с правильным контекстом group."""
        response = self.author_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug'})
        )
        group = response.context['group']
        self.assertEqual(group, self.group)

    def test_profile_shows_correct_context_author(self):
        """Шаблон profile сформирован с правильным контекстом author."""
        response = self.author_client.get(
            reverse('posts:profile', kwargs={'username': 'auth'})
        )
        author = response.context['author']
        self.assertEqual(author, PostViewsTests.user)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.author_client.get(
            reverse('posts:post_detail', kwargs={'post_id': 1})
        )
        post = response.context.get('post')
        self.assertEqual(post.author.username, PostViewsTests.user.username)
        self.assertEqual(post.text, PostViewsTests.post.text)
        self.assertEqual(post.group.title, PostViewsTests.group.title)
        form = response.context.get('form')
        verbose_name = (form._meta.model._meta.get_field('text').verbose_name)
        form_field = form.fields['text']
        self.assertEqual(verbose_name, 'Комментарий')
        self.assertIsInstance(form_field, forms.fields.CharField)

    def test_create_post_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = self.author_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': ['Текст поста', forms.fields.CharField],
            'group': ['Группа', forms.fields.ChoiceField]
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form = response.context.get('form')
                verbose_name = (
                    form._meta.model._meta.get_field(value).verbose_name
                )
                form_field = form.fields[value]
                is_edit = response.context.get('is_edit')
                self.assertEqual(verbose_name, expected[0])
                self.assertIsInstance(form_field, expected[1])
                self.assertIsNone(is_edit)

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.author_client.get(
            reverse('posts:post_edit', kwargs={'post_id': 1})
        )
        text_field = response.context.get('form').instance.text
        group_field = response.context.get('form').instance.group.title
        form_fields = {
            'text': [
                'Текст поста',
                forms.fields.CharField,
                text_field,
                'Тестовый пост'
            ],
            'group': [
                'Группа',
                forms.fields.ChoiceField,
                group_field,
                'Тестовая группа'
            ],
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form = response.context.get('form')
                verbose_name = (
                    form._meta.model._meta.get_field(value).verbose_name
                )
                form_field = form.fields[value]
                is_edit = response.context.get('is_edit')
                self.assertEqual(verbose_name, expected[0])
                self.assertIsInstance(form_field, expected[1])
                self.assertEqual(expected[2], expected[3])
                self.assertTrue(is_edit)

    def test_post_with_group_doesnt_show_on_test_slug_2(self):
        """Пост с группой не появляется на странице test-slug-2."""
        response = self.author_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug-2'})
        )
        posts_on_page = len(response.context.get('page_obj').object_list)
        another_group_posts = (
            Post.objects.filter(group=self.another_group).count()
        )
        self.assertEqual(posts_on_page, another_group_posts)

    def test_post_with_image_shows_correct_context(self):
        """При выводе поста с картинкой изображение передаётся
        в словаре context.
        """
        pages_names = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}),
            reverse('posts:profile', kwargs={'username': 'auth'})
        ]
        for name in pages_names:
            with self.subTest(name=name):
                response = self.author_client.get(name)
                page_object = response.context['page_obj'][0]
                self.assertEqual(page_object.image, self.post.image)

    def test_post_detail_with_image_shows_correct_context(self):
        """При выводе поста с картинкой на подробной странице поста
        изображение передаётся в словаре context.
        """
        response = self.author_client.get(
            reverse('posts:post_detail', kwargs={'post_id': 1})
        )
        page_object = response.context.get('post')
        self.assertEqual(page_object.image, self.post.image)

    def test_comment_show_on_post_page(self):
        """Комментарий появляется на странице поста."""
        response = self.author_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk})
        )
        comment = response.context['comments'][0]
        self.assertEqual(comment, PostViewsTests.comment)

    def test_posts_on_index_page_save_in_cache(self):
        """Список записей страницы index хранится в кэше"""
        response = self.author_client.get(reverse('posts:index'))
        content = response.content.decode()
        self.post.delete()
        another_response = self.author_client.get(reverse('posts:index'))
        another_content = another_response.content.decode()
        self.assertEqual(content, another_content)

    def test_profile_follow(self):
        """Авторизованный пользователь может подписываться
        на других пользователей.
        """
        self.authorized_client.get(reverse(
            'posts:profile_follow',
            kwargs={'username': PostViewsTests.user.username})
        )
        self.assertTrue(
            Follow.objects.filter(
                user=self.user,
                author=PostViewsTests.user
            ).exists()
        )

    def test_profile_unfollow(self):
        """Авторизованный пользователь может удалять авторов из подписок."""
        Follow.objects.create(user=self.user, author=PostViewsTests.user)
        self.authorized_client.get(reverse(
            'posts:profile_unfollow',
            kwargs={'username': PostViewsTests.user.username})
        )
        self.assertEqual(Follow.objects.count(), 0)

    def test_post_shows_on_follower_page_and_not_on_unfollower_page(self):
        """Новая запись пользователя появляется в ленте тех,
        кто на него подписан и не появляется в ленте тех, кто не подписан.
        """
        self.authorized_client.get(reverse(
            'posts:profile_follow',
            kwargs={'username': PostViewsTests.user.username})
        )
        response = self.authorized_client.get(reverse('posts:follow_index'))
        follow_post = response.context['page_obj'][0]
        autor_post = PostViewsTests.user.posts.get()
        self.authorized_client.force_login(self.another_user)
        another_response = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        another_follow_post = len(another_response.context['page_obj'])
        self.assertEqual(follow_post, autor_post)
        self.assertEqual(another_follow_post, 0)
