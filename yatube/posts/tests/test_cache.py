from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.core.cache import cache

from posts.models import Post


User = get_user_model()


class PostCacheTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='Author_of_the_post')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_cache_v2(self):
        # 1. создаем посты
        Post.objects.create(
            text='kakoi-to tekst',
            author=self.user
        )
        Post.objects.create(
            text='kakoi-to drugoi tekst',
            author=self.user
        )
        # 2. загружаем страницу и сохраняем в переменную
        page_1 = self.client.get('/')
        # 3. удаляем посты
        Post.objects.all().delete()
        # 4. загружаем страницу и сохраняем в переменную
        page_2 = self.client.get('/')
        # 5. очищаем кеш
        cache.clear()
        # 6. загружаем страницу и сохраняем в переменную
        page_3 = self.client.get('/')
        self.assertEqual(page_1.content, page_2.content)
        self.assertNotEqual(page_1.content, page_3.content)
