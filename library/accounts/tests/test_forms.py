import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "library.settings")
django.setup()

from accounts.forms import RegisterForm
from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()


class LoginFormTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create_user(
            username="user1",
            password="Dl5wlKWN",
            email="user1@email.com",
        )

    def test_username_field_label(self):
        form = RegisterForm()
        expected_label = "Имя пользователя"
        self.assertEqual(form.fields["username"].label, expected_label)

    def test_email_field_label(self):
        form = RegisterForm()
        expected_label = "Адрес электронной почты"
        self.assertEqual(form.fields["email"].label, expected_label)

    def test_password1_field_label(self):
        form = RegisterForm()
        expected_label = "Пароль"
        self.assertEqual(form.fields["password1"].label, expected_label)

    def test_password2_field_label(self):
        form = RegisterForm()
        expected_label = "Подтверждение пароля"
        self.assertEqual(form.fields["password2"].label, expected_label)

    def test_username_field_unique(self):
        data = {
            "username": self.user.username,
            "email": "unique@email.com",
            "password1": "Dl5wlKWN",
            "password2": "Dl5wlKWN",
        }
        form = RegisterForm(data=data)
        self.assertFalse(form.is_valid())

    def test_email_field_unique(self):
        data = {
            "username": "unique",
            "email": self.user.email,
            "password1": "Dl5wlKWN",
            "password2": "Dl5wlKWN",
        }
        form = RegisterForm(data=data)
        self.assertFalse(form.is_valid())

    def test_password_field_mismatch(self):
        data = {
            "username": "unique",
            "email": self.user.email,
            "password1": "Dl5wlKWN",
            "password2": "otherpassword",
        }
        form = RegisterForm(data=data)
        self.assertFalse(form.is_valid())

    def test_username_field_required(self):
        data = {
            "email": "unique@email.com",
            "password1": "Dl5wlKWN",
            "password2": "Dl5wlKWN",
        }
        form = RegisterForm(data=data)
        self.assertFalse(form.is_valid())

    def test_email_field_required(self):
        data = {
            "username": "unique",
            "password1": "Dl5wlKWN",
            "password2": "Dl5wlKWN",
        }
        form = RegisterForm(data=data)
        self.assertFalse(form.is_valid())

    def test_password1_field_required(self):
        data = {
            "username": "unique",
            "email": "unique@email.com",
            "password2": "Dl5wlKWN",
        }
        form = RegisterForm(data=data)
        self.assertFalse(form.is_valid())

    def test_password2_field_required(self):
        data = {
            "username": "unique",
            "email": "unique@email.com",
            "password1": "Dl5wlKWN",
        }
        form = RegisterForm(data=data)
        self.assertFalse(form.is_valid())
