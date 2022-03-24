from django.test import TestCase

from posts.tests import testmodule_constants as constants
from posts.models import Comment, Follow, Group, Post, User


class PostModelTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=constants.USER_NAME)
        cls.user_2 = User.objects.create_user(username=constants.USER_NAME_2)
        cls.group = Group.objects.create(
            title=constants.GROUP_TITLE,
            slug=constants.GROUP_SLUG,
            description=constants.GROUP_DESCRIPTION,
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=constants.POST_TEXT_2,
        )
        cls.follow = Follow.objects.create(
            user=cls.user,
            author=cls.user_2
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            text=constants.COMMENT_TEXT,
            author=cls.user_2
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        self.assertEqual(PostModelTest.post.__str__(), '012345678912345')
        self.assertEqual(PostModelTest.group.__str__(), constants.GROUP_TITLE)

    def test_models_create_proper_objects(self):
        self.assertTrue(
            self.follow.user.username == Follow.objects.get(
                author=self.user_2
            ).user.username
        )
        self.assertTrue(
            self.follow.author.username == Follow.objects.get(
                user=self.user
            ).author.username
        )
        self.assertTrue(
            self.comment.post.id == Comment.objects.get(post=self.post).post.id
        )
