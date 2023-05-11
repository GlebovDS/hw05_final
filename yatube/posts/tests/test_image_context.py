import shutil
import tempfile

from django.test import TestCase, Client, override_settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.core.cache import cache

from posts.models import Post, Group
from posts.forms import PostForm


User = get_user_model()


# # Создаем временную папку для медиа-файлов;
# # на момент теста медиа папка будет переопределена
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostImageAddTests(TestCase):
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
            text='Тест текст',
            author=cls.user,
            group=cls.group,
            image=None
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        super().setUp()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_image_on_the_page(self):
        """Проверка наличия картинки на страницах"""
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'group': self.group.pk,
            'text': 'Тест текст 2. картинка',
            'image': uploaded,
        }
        response_create = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), posts_count + 1)
        latest_post = Post.objects.latest('id')
        # Проверяем поля созданной записи
        self.assertEqual(latest_post.text,
                         'Тест текст 2. картинка')
        self.assertEqual(latest_post.group,
                         self.group)
        self.assertEqual(latest_post.image,
                         'posts/small.gif')
        img_context_create = response_create.context.get('page_obj')[0].image
        testing_pages = [
            reverse('posts:index'),
            reverse('posts:profile',
                    kwargs={'username': self.user}),
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}),
        ]
        for name_page in testing_pages:
            with self.subTest(name_page=name_page):
                response = self.authorized_client.get(name_page)
                img_context_got = response.context.get('page_obj')[0].image
                self.assertEqual(img_context_got, img_context_create.name)
        response = self.authorized_client.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': latest_post.id}))
        img_context_details = response.context.get('posts')[0].image
        self.assertEqual(
            img_context_details,
            img_context_create
        )
