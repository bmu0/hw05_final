import shutil
import tempfile


from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from posts.tests import testmodule_constants as constants
from posts.models import Comment, Group, Post, User
from yatube import settings

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
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
        cls.small = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.image = SimpleUploadedFile(
            name='image.gif',
            content=cls.small,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            text=constants.POST_TEXT,
            group=PostsFormsTests.group,
            author=cls.user
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'text',
            'group': PostsFormsTests.group.pk,
            'image': self.image,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        post_order = Post.objects.order_by('id').last()
        self.assertEqual(post_order.image.name, 'posts/' + 'image.gif')
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
