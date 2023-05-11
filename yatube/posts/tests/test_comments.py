from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from posts.models import Post, Group
from posts.forms import CommentForm


User = get_user_model()


class CommentsTests(TestCase):
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
            text='Тест текст первого поста',
            author=cls.user,
            group=cls.group
        )
        cls.form = CommentForm()

    def setUp(self):
        super().setUp()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_guest_can_not_to_comment(self):
        """
        Неавтор-ный пользователь (гость) не может
        оставлять комменты, редиректится на страницу входа
        """
        form_data = {
            'text': 'Тестовый комментарий',
        }
        response = self.client.post(
            reverse('posts:add_comment',
                    kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertTemplateUsed(response, 'users/login.html')

    def test_auth_user_can_to_comment(self):
        """
        Авторизованный юзер может комментировать,
        комментарий появляется на странице поста
        """
        form_data = {
            'text': 'Тестовый комментарий',
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment',
                    kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        # Проверка редиректа после отправки коммента
        self.assertRedirects(
            response,
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post.id}),
        )
        # Проверка появления комментария на странице
        self.assertEqual(
            response.context.get('comments')[0].text,
            'Тестовый комментарий')

    def test_redir_not_author(self):
        """
        Авторизованного пользователя, но не автора, перенаправляет на
        страницу просмотра поста, при попытке редактировать его
        """
        # Создаем и логиним нового юзера
        self.user_2 = User.objects.create_user(username='Some_User')
        self.authorized_client_2 = Client()
        self.authorized_client_2.force_login(self.user_2)
        response = self.authorized_client_2.get(
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.id})
        )
        # Проверяем редирект
        self.assertRedirects(
            response,
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post.id})
        )
