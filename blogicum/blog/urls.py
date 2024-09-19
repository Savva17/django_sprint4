from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.BlogListView.as_view(), name='index'),
    path('posts/<int:post_id>/',
         views.PostDetailView.as_view(), name='post_detail'),
    path('posts/<int:post_id>/edit/',
         views.PostEditUpdateView.as_view(), name='edit_post'),
    path('posts/<int:post_id>/delete/',
         views.PostDeleteView.as_view(), name='delete_post'),
    path('posts/create/', views.PostCreateView.as_view(), name='create_post'),
    path('posts/<int:post_id>/comment/',
         views.AddCommentView.as_view(), name='add_comment'),
    path('posts/<int:post_id>/edit_comment/<comment_id>/',
         views.EditCommentView.as_view(), name='edit_comment'),
    path('posts/<int:post_id>/delete_comment/<comment_id>/',
         views.CommentDeleteView.as_view(), name='delete_comment'),
    path('category/<slug:category_slug>/',
         views.CategoryListView.as_view(), name='category_posts'),
    path('profile/edit/',
         views.ProfileUpdateView.as_view(), name='edit_profile'),
    path('profile/<str:username>/',
         views.UserProfileView.as_view(), name='profile'),
]
