from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django import forms

User = get_user_model()


class CreationForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=12,
        min_length=4,
        required=True,
        label='Имя',
        help_text='Обязательное поле. Имя'
    )
    last_name = forms.CharField(
        max_length=12,
        min_length=4,
        required=True,
        label='Фамилия',
        help_text='Обязательное поле. Фамилия',
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')
