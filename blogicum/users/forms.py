from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.forms import ModelForm

User = get_user_model()


'''class CustomUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):

        model = User'''

class UserForm(ModelForm):

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'password')
