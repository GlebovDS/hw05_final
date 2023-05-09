from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.cache import cache

from posts.models import Post, Group


NUMB_OF_POSTS = 10


User = get_user_model()


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Author_of_the_post')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        Post.objects.bulk_create(
            [
                Post(
                    text=f'Тестовый текст для поста {i}',
                    author=cls.user,
                    group=cls.group
                ) for i in range(NUMB_OF_POSTS + 3)
            ]
        )

    def setUp(self):
        super().setUp()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_first_page_contains_ten_records(self):
        """Проверка: количество постов на первой странице равно 10."""
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_records(self):
        """Проверка: на второй странице должно быть 3 поста."""
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_first_page_group_list_contains_ten_records(self):
        """
        Проверка: количество постов на первой странице group_list равно 10.
        """
        response = self.client.get(
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug})
        )
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_group_list_contains_three_records(self):
        """Проверка: на второй странице group_list должно быть 3 поста."""
        response = self.client.get(
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}
                    ) + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_first_page_profile_contains_ten_records(self):
        """
        Проверка: количество постов на первой странице profile равно 10.
        """
        response = self.client.get(
            reverse('posts:profile',
                    kwargs={'username': self.user})
        )
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_profile_contains_three_records(self):
        """Проверка: на второй странице profile должно быть 3 поста."""
        response = self.client.get(
            reverse('posts:profile',
                    kwargs={'username': self.user}
                    ) + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 3)
