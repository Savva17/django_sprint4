from django.utils import timezone

from blog.models import Post


def get_filter_posts(category=None):
    """
    Возвращает отфильтрованный список постов.
    Если указана категория, фильтрует по категории.
    """
    current_time = timezone.now()
    filters = {
        'is_published': True,
        'pub_date__lte': current_time,
        'category__is_published': True,
    }
    if category:
        filters['category'] = category

    return Post.objects.filter(**filters)
