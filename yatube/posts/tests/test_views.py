import os
from datetime import datetime
import time

from django.test import TestCase, Client
from django.urls import reverse
from django.forms import fields
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key

from posts.tests import testmodule_constants as constants
from posts.models import Follow, Group, Post, User
from yatube import settings


class PostsViewTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=constants.USER_NAME)
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.image = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )

        cls.group = Group.objects.create(
            title=constants.GROUP_TITLE,
            slug=constants.GROUP_SLUG,
            description=constants.GROUP_DESCRIPTION,
        )
        cls.post = Post.objects.create(
            text=constants.POST_TEXT,
            group=PostsViewTests.group,
            author=cls.user,
            image=cls.image
        )
        cls.url_templates_logged_in = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': f'{cls.group.slug}'}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile', kwargs={'username': cls.user.username}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': cls.post.pk}
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit', kwargs={'post_id': cls.post.pk}
            ): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }

    @classmethod
    def tearDownClass(cls):
        # я это в интернетах нашел, я не знаю насколько это норма вообще
        images_path = os.path.join(settings.BASE_DIR, 'media/posts')
        files = [
            i for i in os.listdir(images_path)
            if os.path.isfile(os.path.join(images_path, i))
            and i.startswith('small')
        ]
        files_2 = [
            i for i in os.listdir(images_path)
            if os.path.isfile(os.path.join(images_path, i))
            and i.startswith('image')
        ]
        for file in files:
            os.remove(os.path.join(images_path, file))
        for file in files_2:
            os.remove(os.path.join(images_path, file))

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for reverse_name, template in self.url_templates_logged_in.items():
            with self.subTest(reverse_name=reverse_name):
                if (
                    reverse_name == reverse(
                        'posts:post_edit',
                        kwargs={'post_id': self.post.pk}
                    )
                    and self.post.author != self.user
                ):
                    template = 'posts/post_detail.html'
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        text = first_object.text
        group = first_object.group
        author = first_object.author
        image = first_object.image
        self.assertEqual(text, 'Тестовый текст')
        self.assertEqual(group.title, 'Тестовый заголовок')
        self.assertEqual(author, self.user)
        self.assertEqual(image.name, 'posts/' + self.image.name)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = (self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': constants.GROUP_SLUG}
            )
        ))
        first_object = response.context['page_obj'][0]
        text = first_object.text
        group = first_object.group
        author = first_object.author
        image = first_object.image
        self.assertEqual(text, 'Тестовый текст')
        self.assertEqual(group.slug, constants.GROUP_SLUG)
        self.assertEqual(author, self.user)
        self.assertEqual(image.name, 'posts/' + self.image.name)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = (self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user.username}))
        )
        first_object = response.context['page_obj'][0]
        text = first_object.text
        group = first_object.group
        author = first_object.author.username
        image = first_object.image
        self.assertEqual(text, 'Тестовый текст')
        self.assertEqual(group.slug, constants.GROUP_SLUG)
        self.assertEqual(author, self.user.username)
        self.assertEqual(image.name, 'posts/' + self.image.name)

    def test_post_detail_pages_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = (self.authorized_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': self.post.pk}
        )))
        self.assertEqual(
            response.context.get('post').text, 'Тестовый текст'
        )
        self.assertEqual(
            response.context.get('post').group.slug, constants.GROUP_SLUG
        )
        self.assertEqual(
            response.context.get('post').author.username, self.user.username
        )
        self.assertEqual(
            response.context.get('post').image.name, 'posts/' + self.image.name
        )

    def test_post_create_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': fields.CharField,
            'group': fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = (self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}))
        )
        form_fields = {
            'text': fields.CharField,
            'group': fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_index_cache_works(self):
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        key = make_template_fragment_key(
            'index_page',
            [response.context['page_obj']]
        )
        self.assertTrue(first_object)
        Post.objects.all().delete()
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertTrue(first_object)
        self.assertTrue(cache.get(key))
        cache.clear()
        self.assertFalse(cache.get(key))


class PaginatorViewsTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()
        cls.user = User.objects.create_user(username=constants.USER_NAME_2)
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.group = Group.objects.create(
            title=constants.GROUP_TITLE_2,
            slug=constants.GROUP_SLUG_2,
            description=constants.GROUP_DESCRIPTION,
        )
        for i in range(25):
            Post.objects.create(
                text='Тестовый текст',
                group=PaginatorViewsTest.group,
                author=cls.user
            )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            group=PaginatorViewsTest.group,
            author=cls.user
        )

    def test_first_index_page_contains_ten_records(self):
        response = (self.client.get(reverse(
            'posts:group_list', kwargs={'slug': constants.GROUP_SLUG_2}
        )))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_third_index_page_contains_three_records(self):
        response = (self.client.get(reverse(
            'posts:group_list',
            kwargs={'slug': constants.GROUP_SLUG_2}
        ) + '?page=3'))
        self.assertEqual(len(response.context['page_obj']), 6)

    def test_first_group_page_contains_ten_records(self):
        response = (self.client.get(reverse(
            'posts:group_list',
            kwargs={'slug': constants.GROUP_SLUG_2}
        )))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_third_group_page_contains_three_records(self):
        response = (self.client.get(reverse(
            'posts:group_list',
            kwargs={'slug': constants.GROUP_SLUG_2}
        ) + '?page=3'))
        self.assertEqual(len(response.context['page_obj']), 6)

    def test_first_author_page_contains_ten_records(self):
        response = (self.client.get(
            reverse('posts:profile', kwargs={'username': self.user.username}))
        )
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_third_author_page_contains_three_records(self):
        response = (self.client.get(reverse(
            'posts:profile',
            kwargs={'username': self.user.username}
        ) + '?page=3'))
        self.assertEqual(len(response.context['page_obj']), 6)


class FollowViewsTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=constants.USER_NAME_4)
        cls.user_2 = User.objects.create_user(username=constants.USER_NAME_5)
        cls.user_3 = User.objects.create_user(username=constants.USER_NAME_6)
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title=constants.GROUP_TITLE_2,
            slug=constants.GROUP_SLUG_2,
            description=constants.GROUP_DESCRIPTION,
        )
        for i in range(25):
            Post.objects.create(
                text=constants.POST_TEXT,
                group=cls.group,
                author=cls.user
            )
        cls.post = Post.objects.create(
            text=constants.POST_TEXT_2,
            group=cls.group,
            author=cls.user_2
        )
        cls.follow = Follow.objects.create(
            user=cls.user_3,
            author=cls.user
        )

    def test_follow_creates_deletes_and_shows_correct_follows(self):
        self.authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.user_2.username}
            )
        )
        response = self.authorized_client.get(
            reverse(
                'posts:follow_index'
            ),
            follow=True
        )
        new_follow = Follow.objects.filter(user=self.user)
        another_follow = Follow.objects.get(user=self.user_3)
        first_object = response.context['page_obj'][0]
        self.assertTemplateUsed(
            response,
            'posts/follow.html'
        )
        self.assertTrue(new_follow.count() == 1)
        self.assertTrue(new_follow[0].author.username == constants.USER_NAME_5)
        self.assertTrue(
            another_follow.author.username == constants.USER_NAME_4
        )
        self.assertFalse(first_object.text == constants.POST_TEXT)
        self.assertEqual(first_object.text, constants.POST_TEXT_2)
        self.authorized_client.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.user_2.username}
            )
        )
        deleted_follow_count = Follow.objects.filter(user=self.user).count()
        self.assertTrue(deleted_follow_count == 0)

    def test_self_sub(self):
        # самоподписка
        self.authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.user.username}
            )
        )
        new_follow = Follow.objects.filter(user=self.user)
        # самоподписка не создалась
        self.assertTrue(new_follow.count() == 0)


class SergeyTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoNameLol')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='тестовый пост',
            group=cls.group,
        )
        cls.post_2 = Post.objects.create(
            author=cls.user,
            text='тестовый пост номер 2',
            group=cls.group,
        )
        cls.post_3 = Post.objects.create(
            author=cls.user,
            text='тестовый пост номер 3',
            group=cls.group,
        )
        cls.post_4 = Post.objects.create(
            author=cls.user,
            text='тестовый пост номер 4',
        )
        cls.post_5 = Post.objects.create(
            author=cls.user,
            text='тестовый пост номер 5',
            group=cls.group,
        )
        cls.post_6 = Post.objects.create(
            author=cls.user,
            text='тестовый пост номер 6',
            group=cls.group,
        )
        cls.post_7 = Post.objects.create(
            author=cls.user,
            text='тестовый пост номер 7',
            group=cls.group,
        )
        cls.post_8 = Post.objects.create(
            author=cls.user,
            text='тестовый пост номер 8',
            group=cls.group,
        )
        cls.post_9 = Post.objects.create(
            author=cls.user,
            text='тестовый пост номер 9',
            group=cls.group,
        )
        cls.post_10 = Post.objects.create(
            author=cls.user,
            text='тестовый пост номер 10',
            group=cls.group,
        )
        cls.post_11 = Post.objects.create(
            author=cls.user,
            text='тестовый пост номер 11',
            group=cls.group,
        )
        cls.post_12 = Post.objects.create(
            author=cls.user,
            text='тестовый пост номер 12',
            group=cls.group,
        )
        cls.post_13 = Post.objects.create(
            author=cls.user,
            text='тестовый пост номер 13',
            group=cls.group,
        )
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Собираем в словарь пары "имя_html_шаблона: reverse(name)"
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': (
                reverse('posts:group_list', kwargs={'slug': 'slug'})
            ),
            'posts/profile.html': (
                reverse('posts:profile', kwargs={'username': 'HasNoNameLol'})
            ),
            'posts/post_detail.html': (
                reverse('posts:post_detail', kwargs={'post_id': '1'})
            ),
            'posts/create_post.html': (
                reverse('posts:post_edit', kwargs={'post_id': '1'})
            ),
            'posts/create_post.html': reverse('posts:post_create'),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = SergeyTests.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым
        
        first_object = response.context['page_obj'][0]
        post_author_0 = first_object.author.username
        post_pub_date = datetime.date(first_object.created)
        post_group = first_object.group.title
        post_text = first_object.text
        self.assertEqual(post_author_0, 'HasNoNameLol')
        self.assertEqual(post_pub_date, datetime.today().date())
        self.assertEqual(post_group, 'Тестовая группа')
        self.assertEqual(post_text, 'тестовый пост номер 13')

    def test_first_page_contains_ten_records(self):
        response = self.client.get(reverse('posts:index'))
        # Проверка: количество постов на первой странице равно 10.
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_records(self):
        # Проверка: на второй странице должно быть три поста.
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 4)

    def test_group_posts_page_show_correct_context(self):
        """Шаблон group_posts сформирован с правильным контекстом."""
        response = (
            self.authorized_client.
            get(reverse('posts:group_list', kwargs={'slug': 'slug'}))
        )
        self.assertEqual(
            response.context.get('group').title, 'Тестовая группа'
        )
        self.assertEqual(
            response.context.get('group').description, 'Тестовое описание'
        )
        self.assertEqual(response.context.get('group').slug, 'slug')

    def test_first_group_page_contains_ten_records(self):
        response = (
            self.client.get(
                reverse('posts:group_list', kwargs={'slug': 'slug'})
            )
        )
        # Проверка: количество постов на первой странице равно 10.
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_group_page_contains_two_records(self):
        # Проверка: на второй странице должно быть три поста.
        response = (
            self.client.get(
                reverse(
                    'posts:group_list', kwargs={'slug': 'slug'}) + '?page=2'
            )
        )
        self.assertEqual(len(response.context['page_obj']), 2)

    def test_profile_page_show_correct_context(self):
        """Шаблон group_posts сформирован с правильным контекстом."""
        response = (
            self.authorized_client.get(
                reverse('posts:profile', kwargs={'username': 'HasNoNameLol'})
            )
        )
        self.assertEqual(response.context.get('author').username, 'HasNoNameLol')

    def test_first_profile_page_contains_ten_records(self):
        response = (
            self.client.get(
                reverse('posts:profile', kwargs={'username': 'HasNoNameLol'})
            )
        )
        # Проверка: количество постов на первой странице равно 10.
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_profile_page_contains_three_records(self):
        # Проверка: на второй странице должно быть три поста.
        response = (
            self.client.get(
                reverse(
                    'posts:profile',
                    kwargs={'username': 'HasNoNameLol'}) + '?page=2'
            )
        )
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_post_detail_page_show_correct_context(self):
        # Проверка: на второй странице должно быть три поста.
        response = (
            self.client.get(
                reverse('posts:post_detail', kwargs={'post_id': '1'})
            )
        )
        self.assertEqual(response.context.get('post').text, 'Тестовый текст')
        self.assertEqual(
            response.context.get('post').group.title, 'Тестовый заголовок'
        )
        self.assertEqual(
            response.context.get('post').author.username, 'HasNoName'
        )

    def test_create_page_show_correct_context(self):
        """Шаблон сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        # Словарь ожидаемых типов полей формы:
        # указываем, объектами какого класса должны быть поля формы
        form_fields = {
            'text': fields.CharField,
            'group': fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(form_field, expected)
