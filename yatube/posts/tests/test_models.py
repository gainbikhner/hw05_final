from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Comment, Follow, Group, Post, Word

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
        self.assertEqual(str(self.post), self.post.text[:NUMBER_OF_LETTERS])

    def test_verbose_names(self):
        """verbose_name в полях совпадает с ожидаемым."""
        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа'
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).verbose_name,
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

    def test_verbose_names(self):
        """verbose_name в полях совпадает с ожидаемым."""
        field_verboses = {
            'title': 'Название',
            'slug': 'Адрес',
            'description': 'Описание'
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.group._meta.get_field(field).verbose_name,
                    expected_value
                )


class CommentModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост'
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Тестовый комментарий'
        )

    def test_model_have_correct_object_name(self):
        """Проверяем, что у модели Comment корректно работает __str__."""
        self.assertEqual(
            str(self.comment),
            self.comment.text[:NUMBER_OF_LETTERS]
        )

    def test_verbose_names(self):
        """verbose_name в полях совпадает с ожидаемым."""
        field_verboses = {
            'text': 'Комментарий',
            'created': 'Дата публикации',
            'author': 'Автор',
            'post': 'Пост'
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.comment._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_help_texts(self):
        """help_text в полях совпадает с ожидаемым."""
        self.assertEqual(
            self.comment._meta.get_field('text').help_text,
            'Введите комментарий'
        )


class FollowModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.author = User.objects.create_user(username='author')
        cls.follow = Follow.objects.create(user=cls.user, author=cls.author)

    def test_model_have_correct_object_name(self):
        """Проверяем, что у модели Follow корректно работает __str__."""
        follow = self.follow
        self.assertEqual(str(follow), f'{follow.user} follows {follow.author}')

    def test_verbose_names(self):
        """verbose_name в полях совпадает с ожидаемым."""
        field_verboses = {'user': 'Подписчик', 'author': 'Автор'}
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.follow._meta.get_field(field).verbose_name,
                    expected_value
                )


class WordModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.word = Word.objects.create(word='Слово')

    def test_model_have_correct_object_name(self):
        """Проверяем, что у модели Word корректно работает __str__."""
        self.assertEqual(str(self.word), self.word.word)

    def test_verbose_names(self):
        """verbose_name в поле совпадает с ожидаемым."""
        self.assertEqual(
            self.word._meta.get_field('word').verbose_name,
            'Запретное слово'
        )
