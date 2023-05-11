from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.cache import cache

from posts.models import Post


User = get_user_model()


class PostCacheTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='Author_of_the_post')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        # cache.clear()

    # def test_cache(self):
    #     """Проверка правильной работы кеширования"""
    #     response = self.authorized_client.get(reverse('posts:index'))
    #     empty_db = response.context.get('post')
    #     # Проверяю, что постов нет
    #     self.assertEqual(empty_db, None)
    #     cache.clear()
    #     self.post = Post.objects.create(
    #         text='Testoviy tekst',
    #         author=self.user,
    #     )
    #     response_2 = self.authorized_client.get(reverse('posts:index'))
    #     first_object = response_2.context['page_obj'][0]
    #     # Проверяю, что новый пост есть в обнуленном кеше
    #     self.assertEqual(first_object.text, self.post.text)

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
        # Post.objects.all().delete()
        # 4. загружаем страницу и сохраняем в переменную
        page_2 = self.client.get('/')

        self.assertEqual(page_1, page_2)

        # 5. очищаем кеш
        # cache.clear()
        # 6. загружаем страницу и сохраняем в переменную
        # response_3 = self.client.get(reverse('posts:index'))
        # self.assertEqual(response_1, response_2)











        # self.assertEqual(response_2, response_3)




        # self.assertEqual(response_1.context, response_3.context)





        # count = Post.objects.all()
        # print(count)


        # count = Post.objects.all()
        # print(count)
