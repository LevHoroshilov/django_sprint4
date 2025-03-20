from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path('<slug:username>', views.user_page, name='user_page'),
]