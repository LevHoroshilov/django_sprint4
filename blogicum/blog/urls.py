from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.PostListView.as_view(), name='index'),
    path('create/', views.PostCreateView.as_view(), name='create_post'),
    path('posts/<int:id>/', views.post_detail, name='post_detail'),
    path('posts/<int:id>/edit/', views.func, name='edit_post'),
    path('posts/<int:id>/delete', views.func, name='delete_post'),


    path('posts/<int:id>/comment', views.CommentCreateView.as_view(), name='add_comment'),
    path('posts/<int:id>/edit_comment/<int:comment_id>/', views.edit_comment, name='edit_comment'),
    path('posts/<int:id>/delete_comment/<int:comment_id>/', views.CommentDeleteView.as_view(), name='delete_comment'),
    


    path('profile/<str:username>/', views.user_page, name='profile'),
    path('category/<slug:category_slug>/', views.category_posts, name='category_posts'),
]

