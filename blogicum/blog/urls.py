from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.create, name='create_post'),
    path('posts/<int:id>/', views.post_detail, name='post_detail'),
    path('profile/<str:username>/', views.user_page, name='profile'),
    path('category/<slug:category_slug>/', views.category_posts, name='category_posts'),
]
