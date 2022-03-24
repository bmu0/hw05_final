from django.test import TestCase, Client
from django.urls import reverse

from posts.tests import testmodule_constants as constants
from posts.models import Comment, Group, Post, User


class PostsFormsTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest = Client()
        cls.user = User.objects.create_user(username=constants.USER_NAME)
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title=constants.GROUP_TITLE,
            slug=constants.GROUP_SLUG,
            description=constants.GROUP_DESCRIPTION,
        )
        cls.post = Post.objects.create(
            text=constants.POST_TEXT,
            group=PostsFormsTests.group,
            author=cls.user
        )

    def test_create_post(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'text',
            'group': PostsFormsTests.group.pk,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data
        )
        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': f'{self.user}'})
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                group=PostsFormsTests.group,
                text='text',
            ).exists()
        )
        self.assertTrue(
            Post.objects.filter(
                group=PostsFormsTests.group,
                text='text',
            ).reverse()[0] == Post.objects.latest('created')
        )

    def test_edit_post(self):
        post_id = self.post.pk
        posts_count = Post.objects.count()
        form_data = {
            'group': PostsFormsTests.group.pk,
            'text': 'another text',
        }
        self.authorized_client.post(
            reverse('posts:post_edit', args=(f'{post_id}',)),
            data=form_data,
            follow=False
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(
            Post.objects.filter(
                group=PostsFormsTests.group,
                text='another text',
            ).exists()
        )

    def test_guest_can_add_comment(self):
        comment_count = self.post.comments.count()
        post_id = self.post.pk
        form_data = {
            'post': self.post,
            'text': constants.POST_TEXT
        }
        comments_count = Comment.objects.filter(post=self.post).count()
        self.assertTrue(comments_count == 0)
        self.guest.post(
            reverse('posts:add_comment', args=(f'{post_id}',)),
            data=form_data
        )
        self.assertTrue(
            self.post.comments.count() == comment_count
        )

    def test_user_can_add_comment(self):
        comment_count = self.post.comments.count()
        post_id = self.post.pk
        form_data = {
            'post': self.post,
            'text': constants.POST_TEXT_2
        }
        self.authorized_client.post(
            reverse('posts:add_comment', args=(f'{post_id}',)),
            data=form_data
        )
        comments_count = Comment.objects.filter(post=self.post).count()
        last_comment = self.post.comments.reverse()[0]
        self.assertTrue(
            self.post.comments.count() == comment_count + 1
        )
        self.assertEqual(
            last_comment.text, constants.POST_TEXT_2
        )
        self.assertTrue(comments_count == 1)
