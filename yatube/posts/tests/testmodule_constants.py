from pytils.translit import slugify


GROUP_DESCRIPTION = '1234567890123456789'

GROUP_TITLE = 'Тестовый заголовок'
GROUP_TITLE_2 = 'test title'

GROUP_SLUG = slugify(GROUP_TITLE)[:100]
GROUP_SLUG_2 = slugify(GROUP_TITLE_2)[:100]

POST_TEXT = 'Тестовый текст'

POST_TEXT_2 = '01234567891234567890'

USER_NAME = 'HasNoName'
USER_NAME_2 = 'SuperPuperUser'

URLS_FOR_USER = {
    '/': 'posts/index.html',
    f'/group/{GROUP_SLUG}/': 'posts/group_list.html',
    '/create/': 'posts/create_post.html',
    '/unexisting_page/': 'core/404.html',
}

URLS_FOR_GUEST = {
    '/': 'posts/index.html',
    f'/group/{GROUP_SLUG}/': 'posts/group_list.html',
    '/create/': 'users/login.html',
    '/unexisting_page/': 'core/404.html',
}
