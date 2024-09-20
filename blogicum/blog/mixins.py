from django.urls import reverse
from django.core.exceptions import PermissionDenied

from .models import Comment


class CommentMixin:
    model = Comment
    template_name = 'blog/comment.html'


class SuccessUrlMixin:
    def get_success_url(self):
        return reverse(
            'blog:post_detail', kwargs={'post_id': self.kwargs['post_id']})


class GetObjectMixin:
    def get_object(self, queryset=None):
        comment = super().get_object(queryset)
        if comment.author != self.request.user:
            raise PermissionDenied(
                "Вы не можете редактировать или удалять этот комментарий."
            )
        return comment
