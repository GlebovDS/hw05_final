from http import HTTPStatus

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.cache import cache

from posts.models import Post, Group


User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Author_of_the_post')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
        )

    def setUp(self):
        super().setUp()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.post.author)
        cache.clear()

    def test_post_edit_template(self):
        """Проверка использования верного шаблона при /post/post_id/edit/"""
        editable_post_id = self.post.id
        response = self.authorized_client.get(
            reverse('posts:post_edit', args=[editable_post_id])
        )
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_post_edit_status_code(self):
        """Проверка доступности урла при /post/<post_id>/edit/"""
        editable_post_id = self.post.id
        response = self.authorized_client.get(
            reverse('posts:post_edit', args=[editable_post_id])
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_only_author(self):
        """Пост редактировать может только его автор"""
        editable_post_id = self.post.id
        # Создаем и логиним другого пользователя
        self.some_user = User.objects.create_user(username='Another_user')
        self.authorized_client_2 = Client()
        self.authorized_client_2.force_login(self.some_user)
        response = self.authorized_client_2.get(
            reverse('posts:post_edit', args=[editable_post_id])
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        response_redirect = self.client.get(
            reverse('posts:post_detail', args=[editable_post_id])
        )
        self.assertTemplateUsed(response_redirect, 'posts/post_detail.html')

    def test_public_urls_status_code(self):
        """Проверка доступности общедоступных адресов ."""
        pages_list = {
            '/': HTTPStatus.OK,
            '/unexisting_page/': HTTPStatus.NOT_FOUND,
            f'/group/{self.group.slug}/': HTTPStatus.OK,
            f'/profile/{self.post.author}/': HTTPStatus.OK,
            f'/posts/{self.post.id}/': HTTPStatus.OK,
        }
        for page, expected_status in pages_list.items():
            with self.subTest(page=page):
                response = self.client.get(page)
                self.assertEqual(response.status_code, expected_status)

    def test_post_public_urls_uses_correct_templates(self):
        """URL-адрес использует соответствующий шаблон."""
        # Шаблоны по адресам
        templates_url_names = {
            'posts/index.html': '/',
            'posts/group_list.html': f'/group/{self.group.slug}/',
            'posts/profile.html': f'/profile/{self.user.username}/',
            'posts/post_detail.html': f'/posts/{self.post.id}/',
        }
        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertTemplateUsed(response, template)

    def test_post_create_url_exists_at_desired_location(self):
        """Страница create/ доступна авторизованному пользователю."""
        response = self.authorized_client.get('/create/')
        guest_response = self.client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)
        # Страница недоступна неавторизованному пользователю, редиректит.
        self.assertEqual(guest_response.status_code, HTTPStatus.FOUND)

    def test_post_create_url_uses_correct_template(self):
        """Страница create/ использует шаблон posts/create_post.html"""
        response = self.authorized_client.get('/create/')
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_error_404_template(self):
        """Проверка вызова кастомной страницы для ошибки 404"""
        response = self.client.get('/some_unexpected_page/')
        self.assertTemplateUsed(response, 'core/404.html')
