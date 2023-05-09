from django import forms
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.cache import cache

from posts.models import Post, Group


User = get_user_model()


class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Author_of_the_post')
        cls.group_1 = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post_1 = Post.objects.create(
            text='Тест текст первого поста',
            author=cls.user,
            group=cls.group_1
        )

    def setUp(self):
        super().setUp()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_correct_templates(self):
        """URL-адрес использует соответствующий шаблон"""
        id = self.post_1.id
        username = self.user.username
        group_slug = self.group_1.slug
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    args=[group_slug]): 'posts/group_list.html',
            reverse('posts:profile',
                    args=[username]): 'posts/profile.html',
            reverse('posts:post_detail',
                    args=[id]): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit',
                    args=[id]): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author
        self.assertEqual(post_text_0, self.post_1.text)
        self.assertEqual(post_author_0, self.user)

    def test_group_list_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        self.group_2 = Group.objects.create(
            title='Тестовая группа №2',
            slug='test_slug_2',
            description='Тестовое описание второй группы',
        )
        self.post_2 = Post.objects.create(
            text='Тест текст второго поста',
            author=self.user,
            group=self.group_2
        )
        self.post_3 = Post.objects.create(
            text='Тест текст третьего поста',
            author=self.user,
        )
        self.post_4 = Post.objects.create(
            text='Тест текст 4 поста',
            author=self.user,
            group=self.group_2
        )
        response_1 = (self.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': self.group_1.slug})))
        group_object_list = response_1.context.get('page_obj').object_list
        group_from_context = response_1.context.get('group')
        self.assertEqual(group_object_list[0], self.post_1)
        self.assertEqual(group_from_context, self.group_1)
        response_2 = (self.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': self.group_2.slug})))
        group_object_list_2 = response_2.context.get('page_obj').object_list
        group_from_context_2 = response_2.context.get('group')
        self.assertEqual(group_object_list_2[1], self.post_2)
        self.assertEqual(group_object_list_2[0], self.post_4)
        self.assertEqual(group_from_context_2, self.group_2)

    def test_profile_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        self.user_2 = User.objects.create_user(username='Author_2')
        self.post_2 = Post.objects.create(
            text='Тест текст второго поста',
            author=self.user,
        )
        self.post_3 = Post.objects.create(
            text='Тест текст третьего поста',
            author=self.user_2,
        )
        response = (self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': self.user})))
        profile_object_list = response.context.get('page_obj').object_list
        profile_author = response.context.get('author')
        self.assertEqual(profile_object_list[1], self.post_1)
        self.assertEqual(profile_object_list[0], self.post_2)
        self.assertEqual(profile_author, self.post_1.author)
        response_2 = (self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': self.user_2})))
        profile_object_list_2 = response_2.context.get('page_obj').object_list
        profile_author_2 = response_2.context.get('author')
        self.assertEqual(profile_object_list_2[0], self.post_3)
        self.assertEqual(profile_author_2, self.post_3.author)

    def test_post_detail_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = (self.authorized_client.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post_1.id})))
        post_detail_context = response.context['post']
        post_id_0 = post_detail_context.id
        self.assertEqual(post_id_0, self.post_1.id)

    def test_create_post_context(self):
        """Шаблон create_post (создание) сформир-н с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
        }
        for value, excepted in form_fields.items():
            with self.subTest(value=value):
                field = response.context.get('form').fields.get(value)
                self.assertIsInstance(field, excepted)

    def test_edit_post_context(self):
        """
        Шаблон edit_post (редактирование) сформир-н с правильным контекстом.
        """
        response = (self.authorized_client.get(
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post_1.id})))
        post_text = response.context['form'].initial['text']
        post_group = response.context['form'].initial['group']
        form_fields = {
            post_text: self.post_1.text,
            post_group: self.post_1.id,
        }
        for value, excepted in form_fields.items():
            with self.subTest(value=value):
                self.assertEqual(value, excepted)

    def test_post_in_right_group(self):
        """Проверка на попадение поста в правильную группу"""
        self.group_2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='test_slug_2',
            description='Тестовое описание второй группы',
        )
        self.post_2 = Post.objects.create(
            text='Тестовый текст второго поста',
            author=self.user,
            group=self.group_2,
        )
        response = (self.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': self.group_2.slug})))
        group_object_list = response.context.get('group')
        self.assertEqual(group_object_list, self.group_2)
