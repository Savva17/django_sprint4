from django.http import Http404
from django.views.generic import (
    ListView, DetailView, CreateView, DeleteView, UpdateView
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404, redirect
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseNotFound
from django.db.models.base import Model as Model
from django.db.models import Count
from django.utils import timezone

from .models import Post, Comment, Category

from .forms import AddPostForm, CommentForm


User = get_user_model()


# Создаём миксин для комментариев
class CommentMixin:
    model = Comment
    template_name = 'blog/comment.html'


class BlogListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = 10

    def get_queryset(self):
        now = timezone.now()
        return Post.objects.filter(
            pub_date__lte=now, is_published=True, category__is_published=True
        ).annotate(comment_count=Count('comments')).order_by('-pub_date')


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def get_success_url(self):
        return reverse('blog:index')

    def test_func(self):
        post = self.get_object()
        # Проверяем, что пользователь является автором или администратором.
        return (self.request.user == post.author or
                self.request.user.is_superuser)


class PostDetailView(DetailView):
    model = Post
    context_object_name = 'post'
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        context['form'] = CommentForm()
        # Добавляем список комментариев к посту
        context['comments'] = Comment.objects.filter(
            post=post).order_by('created_at')
        return context

    def get_object(self):
        post = super().get_object()
        # Проверка публикации поста
        if not post.is_published and self.request.user != post.author:
            raise Http404("Доступ запрещен. Пост снят с публикации.")
        # Проверка, отложена публикация
        if post.pub_date > timezone.now() and self.request.user != post.author:
            raise Http404("Доступ запрещен. Публикация отложена.")
        # Проверка публикации категории
        if not post.category.is_published and self.request.user != post.author:
            raise Http404("Доступ запрещен. Категория снята с публикации.")
        return post


class CategoryListView(ListView):
    template_name = 'blog/category.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        category = get_object_or_404(Category.objects.filter(
            is_published=True
        ), slug=self.kwargs['category_slug'])

        # Возвращаем только опубликованные посты
        return Post.objects.filter(
            category=category,
            is_published=True,
            pub_date__lte=timezone.now()
        ).annotate(comment_count=Count('comments')).order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем категорию в контекст
        context['category'] = get_object_or_404(
            Category, slug=self.kwargs['category_slug']
        )
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = AddPostForm
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile', kwargs={'username': self.request.user.username})

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.author = self.request.user
        self.object.save()
        return super().form_valid(form)


class UserProfileView(ListView):
    model = User
    template_name = 'blog/profile.html'
    context_object_name = 'profile'
    paginate_by = 10

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs['username'])
        return Post.objects.filter(
            author=user
        ).annotate(comment_count=Count('comments')).order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_object_or_404(User, username=self.kwargs['username'])
        context['profile'] = user
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'blog/user.html'
    fields = ['first_name', 'last_name', 'username', 'email']

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse(
            'blog:profile', kwargs={'username': self.request.user.username})


class PostEditUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = AddPostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        post = self.get_object()
        if post.author != self.request.user:
            return redirect('blog:post_detail', post_id=post.pk)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'post_id': self.object.pk})


class AddCommentView(LoginRequiredMixin, CommentMixin, CreateView):
    form_class = CommentForm

    def form_valid(self, form):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        form.instance.author = self.request.user
        form.instance.post = post
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:post_detail', kwargs={'post_id': self.kwargs['post_id']})


class EditCommentView(LoginRequiredMixin, CommentMixin, UpdateView):
    form_class = CommentForm
    pk_url_kwarg = 'comment_id'

    def get_object(self, queryset=None):
        comment = super().get_object(queryset)
        if comment.author != self.request.user:
            raise PermissionDenied(
                "Вы не можете редактировать этот комментарий.")
        return comment

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["post_id"] = self.kwargs['post_id']
        return context

    def get_success_url(self):
        return reverse(
            'blog:post_detail', kwargs={'post_id': self.kwargs['post_id']})


class CommentDeleteView(LoginRequiredMixin, CommentMixin, DeleteView):
    pk_url_kwarg = 'comment_id'

    def get_object(self, queryset=None):
        # Проверяем, что комментарий принадлежит текущему пользователю.
        comment = super().get_object(queryset)
        if comment.author != self.request.user:
            raise PermissionDenied("Вы не можете удалить этот комментарий.")
        return comment

    def get_success_url(self):
        return reverse(
            'blog:post_detail', kwargs={'post_id': self.object.post.id})
