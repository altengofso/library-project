import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "library.settings")
django.setup()

from catalog.models import Author, Book
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class AccountLoginViewTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create_user(
            username="user1",
            password="password1",
            email="user1@email.com",
        )

    def test_url_accessible(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)

    def test_contains_login_form(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue("form" in response.context_data)
        self.assertTrue("username" in response.context_data["form"].fields)
        self.assertTrue("password" in response.context_data["form"].fields)

    def test_successful_login(self):
        response = self.client.post(
            reverse("login"), {"username": "user1", "password": "password1"}
        )
        self.assertRedirects(response, reverse("index"))

    def test_unsuccessful_login(self):
        response = self.client.post(
            reverse("login"), {"username": "user1", "password": "wrong"}
        )
        self.assertGreater(
            len(response.context_data["form"].errors["__all__"]), 0
        )


class AccountProfileViewTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create_user(
            username="user1",
            password="password1",
            email="user1@email.com",
        )
        cls.author = Author.objects.create(
            name="Author 1",
            date_of_birth="1990-01-01",
            bio="Lorem ipsum dolor sit amet",
            photo="authors/photo.jpg",
        )
        cls.books = [
            Book.objects.create(
                title=f"Book {i}",
                author=cls.author,
                summary="Lorem ipsum dolor sit amet",
                publication_year=2023,
                poster=f"posters/book{i}.jpg",
                added_by=cls.user,
            )
            for i in range(15)
        ]
        cls.user2 = User.objects.create_user(
            username="user2",
            password="password2",
            email="user2@email.com",
        )
        cls.books2 = [
            Book.objects.create(
                title=f"Book2 {i}",
                author=cls.author,
                summary="Lorem ipsum dolor sit amet",
                publication_year=2023,
                poster=f"posters/book2{i}.jpg",
                added_by=cls.user2,
            )
            for i in range(30)
        ]

    def test_url_accessible_for_logged_in_user(self):
        self.client.login(username="user1", password="password1")
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 200)

    def test_redirect_for_not_logged_in_user(self):
        response = self.client.get(reverse("profile"))
        self.assertRedirects(
            response, f"{reverse('login')}?next={reverse('profile')}"
        )

    def test_is_paginated(self):
        self.client.login(username="user1", password="password1")
        response = self.client.get(reverse("profile"))
        self.assertTrue("is_paginated" in response.context_data)
        self.assertEqual(response.context_data["is_paginated"], True)
        self.assertEqual(len(response.context_data["object_list"]), 6)

    def test_lists_all_objects_added_by_first_user(self):
        self.client.login(username="user1", password="password1")
        response = self.client.get(reverse("profile"))
        self.assertTrue("paginator" in response.context_data)
        self.assertEqual(response.context_data["paginator"].count, 15)
        self.assertEqual(response.context_data["paginator"].num_pages, 3)

    def test_lists_all_objects_added_by_second_user(self):
        self.client.login(username="user2", password="password2")
        response = self.client.get(reverse("profile"))
        self.assertTrue("paginator" in response.context_data)
        self.assertEqual(response.context_data["paginator"].count, 30)
        self.assertEqual(response.context_data["paginator"].num_pages, 5)


class RegisterUserViewTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create_user(
            username="user1",
            password="password1",
            email="user1@email.com",
        )

    def test_url_redirect_for_logged_in_user(self):
        self.client.login(username="user1", password="password1")
        response = self.client.get(reverse("register"))
        self.assertRedirects(response, reverse("index"))

    def test_redirect_for_not_logged_in_user(self):
        response = self.client.get(reverse("register"))
        self.assertEqual(response.status_code, 200)

    def test_unsuccessful_registration_existing_username(self):
        data = {
            "username": self.user.username,
            "email": "unique@email.com",
            "password1": "Dl5wlKWN",
            "password2": "Dl5wlKWN",
        }
        response = self.client.post(reverse("register"), data)
        self.assertGreater(
            len(response.context_data["form"].errors["username"]), 0
        )

    def test_unsuccessful_registration_existing_email(self):
        data = {
            "username": "unique",
            "email": self.user.email,
            "password1": "Dl5wlKWN",
            "password2": "Dl5wlKWN",
        }
        response = self.client.post(reverse("register"), data)
        self.assertGreater(
            len(response.context_data["form"].errors["email"]), 0
        )

    def test_unsuccessful_registration_password_mismatch(self):
        data = {
            "username": "unique",
            "email": "unique@email.com",
            "password1": "Dl5wlKWN",
            "password2": "other",
        }
        response = self.client.post(reverse("register"), data)
        self.assertGreater(
            len(response.context_data["form"].errors["password2"]), 0
        )

    def test_successful_registration(self):
        data = {
            "username": "unique",
            "email": "unique@email.com",
            "password1": "Dl5wlKWN",
            "password2": "Dl5wlKWN",
        }
        self.client.post(reverse("register"), data)
        self.assertEqual(len(User.objects.filter(username="unique").all()), 1)

    def test_redirect_after_successful_registration(self):
        data = {
            "username": "unique",
            "email": "unique@email.com",
            "password1": "Dl5wlKWN",
            "password2": "Dl5wlKWN",
        }
        response = self.client.post(reverse("register"), data)
        self.assertRedirects(response, reverse("index"))

    def test_autologin_after_successful_registration(self):
        data = {
            "username": "unique",
            "email": "unique@email.com",
            "password1": "Dl5wlKWN",
            "password2": "Dl5wlKWN",
        }
        self.client.post(reverse("register"), data)
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 200)
