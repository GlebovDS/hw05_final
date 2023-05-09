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

    def test_comment(self):
        """
        Проверка на: комментировать посты может только
        авторизованный пользователь.
        """
        form_data = {
            'text': 'Тестовый комментарий',
        }

        response_comment_guest = self.client.post(
            reverse('posts:add_comment',
                    kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        response_comment_auth = self.authorized_client.post(
            reverse('posts:add_comment',
                    kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        guest_context_comment = response_comment_guest.context.get(
            'comments')
        auth_context_comment = response_comment_auth.context.get(
            'comments')[0].text
        # Неавторизованный пользователь не сможет отправить данные
        self.assertIsNone(guest_context_comment)
        # Авторизованный пользователь отправил данные из формы
        self.assertEqual(auth_context_comment, 'Тестовый комментарий')
        comment_sent = response_comment_auth.context.get('comments')[0]
        response_get = self.authorized_client.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post.id})
        )
        comment_got = response_get.context.get('comments')[0]
        # Проверка соответствия отправленного комментария полученному
        self.assertEqual(comment_sent, comment_got)
