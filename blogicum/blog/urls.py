from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.PostListView.as_view(), name='index'),
    path('create/', views.PostCreateView.as_view(), name='create_post'),
    path('posts/<int:pk>/', views.post_detail, name='post_detail'),
    path('posts/<int:id>/edit/', views.PostUpdateView.as_view(), name='edit_post'),
    path('posts/<int:id>/delete/', views.PostDeleteView.as_view(), name='delete_post'),


    path('posts/<int:pk>/comment/', views.CommentCreateView.as_view(), name='add_comment'),
    path('posts/<int:pk>/edit_comment/<int:comment_id>/', views.edit_comment, name='edit_comment'),
    path('posts/<int:pk>/delete_comment/<int:comment_id>/', views.CommentDeleteView.as_view(), name='delete_comment'),
    


    path('profile/<str:username>/', views.user_page, name='profile'),
    path('category/<slug:category_slug>/', views.category_posts, name='category_posts'),
]

