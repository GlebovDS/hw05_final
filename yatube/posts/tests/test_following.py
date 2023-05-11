from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from posts.models import Post, Follow


User = get_user_model()


class FollowingTests(TestCase):
    def setUp(self):
        super().setUp()
        self.user_1 = User.objects.create_user(username='Follower_1')
        self.user_2 = User.objects.create_user(username='Public')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_1)

    def test_following(self):
        """
        Авторизованный пользователь может подписываться на
        других пользователей.
        """
        count = Follow.objects.count()
        self.authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.user_2.username}
            )
        )
        # Проверяем, что подписка создалась
        self.assertTrue(
            Follow.objects.filter(
                user=self.user_1,
                author=self.user_2
            ).exists()
        )
        self.assertEqual(Follow.objects.count(), count + 1)

    def test_unfollowing(self):
        """
        Авторизованный пользователь может отписываться от
        других пользователей.
        """
        # Создаю проверочную подписку
        Follow.objects.get_or_create(
            user=self.user_1,
            author=self.user_2)
        count = Follow.objects.count()
        # Удаляю подписку и проверяю ее отсутствие
        self.authorized_client.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.user_2.username}
            )
        )
        self.assertFalse(
            Follow.objects.filter(
                user=self.user_1,
                author=self.user_2
            ).exists()
        )
        self.assertEqual(Follow.objects.count(), count - 1)

    def test_new_posts_in_feed(self):
        """
        Новая запись пользователя появляется в ленте тех,
        кто на него подписан и не появляется в ленте тех,
        кто не подписан.
        """
        self.post_1 = Post.objects.create(
            text='Тест текст первого поста',
            author=self.user_1,
        )
        self.post_2 = Post.objects.create(
            text='Тест текст второго поста',
            author=self.user_2,
        )
        # Создаю и логиню третьего юзера
        self.user_3 = User.objects.create_user(username='Follower_2')
        self.authorized_client_2 = Client()
        self.authorized_client_2.force_login(self.user_3)
        # Создаю подписку 1-го на 2-го юзера
        Follow.objects.get_or_create(
            user=self.user_1,
            author=self.user_2)
        # Создаю подписку 3-го на 1-го юзера
        Follow.objects.get_or_create(
            user=self.user_3,
            author=self.user_1)
        # Проверяю ленту 1-го юзера
        resp_1 = self.authorized_client.get(
            reverse('posts:follow_index'))
        self.assertEqual(
            resp_1.context['page_obj'][0],
            self.post_2
        )
        # Проверяю ленту 3-го юзера
        resp_2 = self.authorized_client_2.get(
            reverse('posts:follow_index'))
        self.assertEqual(
            resp_2.context['page_obj'][0],
            self.post_1
        )
        # Создаю новый пост вторым юзером
        self.post_3 = Post.objects.create(
            text='Тест текст третьего поста',
            author=self.user_2,
        )
        # Проверяю ленту 1-го юзера на новый пост
        resp_3 = self.authorized_client.get(
            reverse('posts:follow_index'))
        self.assertEqual(
            resp_3.context['page_obj'][0],
            self.post_3
        )
        # Проверяю ленту 3-го юзера на отсутствие нового поста
        resp_4 = self.authorized_client_2.get(
            reverse('posts:follow_index'))
        self.assertEqual(
            resp_4.context['page_obj'][0],
            self.post_1
        )
