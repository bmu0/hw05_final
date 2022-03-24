from http import HTTPStatus

from django.test import TestCase, Client

from posts.tests import testmodule_constants as constants
from posts.models import Group, Post, User


class PostsURLTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.group = Group.objects.create(
            title=constants.GROUP_TITLE,
            slug=constants.GROUP_SLUG,
            description=constants.GROUP_DESCRIPTION,
        )
        cls.post = Post.objects.create(
            text=constants.POST_TEXT,
            group=PostsURLTests.group,
            author=cls.user
        )
        cls.url_templates_logged_in = {
            f'/profile/{cls.user.username}/': 'posts/profile.html',
            f'/posts/{cls.post.pk}/': 'posts/post_detail.html',
            f'/posts/{cls.post.pk}/edit/': 'posts/create_post.html',
            f'/profile/{cls.user.username}/follow/': 'posts/profile.html',
        }
        cls.url_templates_unlogged_in = {
            f'/profile/{cls.user.username}/': 'posts/profile.html',
            f'/posts/{cls.post.pk}/': 'posts/post_detail.html',
            f'/posts/{cls.post.pk}/edit/': 'users/login.html',
            f'/profile/{cls.user.username}/follow/': 'users/login.html',
        }

    def test_dynamic_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for address, template in self.url_templates_logged_in.items():
            with self.subTest(address=address):
                if (
                    address == f'/posts/{self.post.pk}/edit/'
                    and self.post.author != self.user
                ):
                    template = 'posts/post_detail.html'
                response = self.authorized_client.get(address, follow=True)
                self.assertTemplateUsed(response, template)
        for address, template in self.url_templates_unlogged_in.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                if response.status_code == HTTPStatus.FOUND:
                    redirect_url = response.url
                    response = self.guest_client.get(redirect_url)
                self.assertTemplateUsed(response, template)

    def test_ststic_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for address, template in constants.URLS_FOR_USER.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

        for address, template in constants.URLS_FOR_GUEST.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                if response.status_code == HTTPStatus.FOUND:
                    redirect_url = response.url
                    response = self.guest_client.get(redirect_url)
                self.assertTemplateUsed(response, template)
