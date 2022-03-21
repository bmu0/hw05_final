from xml.etree.ElementTree import Comment
from django.forms import ModelForm

from .models import Post, Comment


class PostForm(ModelForm):

    class Meta:
        model = Post
        fields = ['text', 'group', 'image']
        labels = {'Текст': '', 'Группа': '', 'Картинка': ''}


class PostEditForm(ModelForm):

    class Meta:
        model = Post
        fields = ['text', 'group', 'image']
        labels = {'Текст': '', 'Группа': '', 'Картинка': ''}


class CommentForm(ModelForm):

    class Meta:
        model = Comment
        fields = ['text', ]
        labels = {'Текст': ''}
