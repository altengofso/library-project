import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "library.settings")
django.setup()

from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase

User = get_user_model()


class UserModelTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create_user(
            username="user1",
            password="password1",
            email="user1@email.com",
        )

    def test_email_field_unique(self):
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                username="user2",
                password="password2",
                email=self.user.email,
            )
