from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from posts.models import Post, Group


User = get_user_model()


class PostFormsTests(TestCase):
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
            group=cls.group
        )

    def setUp(self):
        super().setUp()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст 2',
            'group': self.group.pk,
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        # Проверяем, что создалась запись
        self.assertTrue(
            Post.objects.filter(
                text=self.post.text,
                group=self.group.pk,
            ).exists()
        )
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), posts_count + 1)

        # Проверяем, сработал ли редирект
        self.assertRedirects(response,
                             reverse('posts:profile',
                                     kwargs={'username': self.user.username}))

    def test_edit_post(self):
        self.group_2 = Group.objects.create(
            title='Вторая тестовая группа',
            slug='test_slug_2',
            description='Тестовое описание второй тестовой группы',
        )
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст отредактирован',
            'group': self.group_2.id,
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('posts:post_edit', args={self.post.pk},),
            data=form_data,
            follow=True
        )
        new_group_id = Post.objects.latest('id').group.id
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(new_group_id, self.group_2.id)
        self.assertRedirects(response,
                             reverse('posts:post_detail',
                                     kwargs={'post_id': self.post.pk},))
