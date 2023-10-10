from django.contrib.auth import forms

from .models import User


class RegisterForm(forms.UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]
