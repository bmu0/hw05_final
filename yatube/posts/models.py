from django.contrib.auth import get_user_model
from django.db import models

from core.models import CreatedModel

User = get_user_model()


class Group(models.Model):
    title = models.CharField('Заголовок', max_length=200)
    slug = models.SlugField('Путь', max_length=200, unique=True)
    description = models.TextField('Описание')

    def __str__(self):
        return(self.title)


class Post(CreatedModel):
    text = models.TextField(
        'Текст',
        help_text='Введите текст'
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='posts'
    )
    group = models.ForeignKey(
        Group,
        verbose_name='Группа',
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name='group_name',
        help_text='Выберите группу'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True,
        null=True,
        help_text='Выберите картинку'
    )

    def __str__(self):
        return self.text[:15]


class Comment(CreatedModel):
    post = models.ForeignKey(
        Post,
        verbose_name='Пост',
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        verbose_name='Юзер',
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name='comments'
    )
    text = models.TextField('Текст комментария', help_text='Введите текст')


class Follow(CreatedModel):
    user = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='follower'
    )
    author = models.ForeignKey(
        User,
        verbose_name='Блоггер',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='following'
    )
