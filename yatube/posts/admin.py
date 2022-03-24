from django.contrib import admin

from .models import Post, Group, Follow, Comment


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('pk', 'text', 'created', 'author', 'group',)
    search_fields = ('text',)
    list_editable = ('group',)
    list_filter = ('created',)
    empty_value_display = '-пусто-'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('pk', 'text', 'created', 'author', 'post',)
    search_fields = ('text', 'author', 'post',)
    list_editable = ('text',)
    list_filter = ('created',)
    empty_value_display = '-пусто-'


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('pk', 'created', 'user', 'author',)
    search_fields = ('user',)
    list_editable = ('user', 'author',)
    list_filter = ('created',)
    empty_value_display = '-пусто-'


admin.site.register(Group)
