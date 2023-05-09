from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.cache import cache

from posts.models import Post


User = get_user_model()


class PostCacheTests(TestCase):
    def setUp(self):
        # super().setUp()
        self.user = User.objects.create_user(username='Author_of_the_post')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_cache(self):
        """Проверка правильной работы кеширования"""
        response = self.authorized_client.get(reverse('posts:index'))
        empty_db = response.context.get('post')
        # Проверяю, что постов нет
        self.assertEqual(empty_db, None)
        cache.clear()
        self.post = Post.objects.create(
            text='Testoviy tekst',
            author=self.user,
        )
        response_2 = self.authorized_client.get(reverse('posts:index'))
        first_object = response_2.context['page_obj'][0]
        # Проверяю, что новый пост есть в обнуленном кеше
        self.assertEqual(first_object.text, self.post.text)
