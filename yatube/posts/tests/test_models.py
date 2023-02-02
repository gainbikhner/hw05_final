from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()

NUMBER_OF_LETTERS = 15


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Длинный тестовый пост'
        )

    def test_model_have_correct_object_name(self):
        """Проверяем, что у модели Post корректно работает __str__."""
        post = self.post
        self.assertEqual(str(post), post.text[:NUMBER_OF_LETTERS])

    def test_verbose_names(self):
        """verbose_name в полях совпадает с ожидаемым."""
        post = self.post
        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа'
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_help_texts(self):
        """help_text в полях совпадает с ожидаемым."""
        field_help_texts = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост'
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).help_text,
                    expected_value
                )


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание'
        )

    def test_model_have_correct_object_name(self):
        """Проверяем, что у модели Group корректно работает __str__."""
        self.assertEqual(str(self.group), self.group.title)
