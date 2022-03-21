from django.contrib import admin

from .models import Post, Group


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('pk', 'text', 'created', 'author', 'group',)
    search_fields = ('text',)
    list_editable = ('group',)
    list_filter = ('created',)
    empty_value_display = '-пусто-'


admin.site.register(Group)