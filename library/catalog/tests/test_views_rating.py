import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "library.settings")
django.setup()

from catalog.models import Author, Book
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class BookRatingViewTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user1 = User.objects.create_user(
            username="user1",
            password="password1",
            email="user1@email.com",
        )
        cls.author = Author.objects.create(
            name="Author",
            date_of_birth="1990-01-01",
            bio="Lorem ipsum dolor sit amet",
            photo="authors/photo.jpg",
        )
        cls.book1 = Book.objects.create(
            title="Book 1",
            author=cls.author,
            summary="Lorem ipsum dolor sit amet",
            publication_year=2023,
            poster="posters/book1.jpg",
            added_by=cls.user1,
        )

    def test_has_rating_form(self):
        response = self.client.get(
            reverse("book-detail", kwargs={"pk": self.book1.pk})
        )
        self.assertTrue("rating_form" in response.context_data)
        self.assertTrue("rate" in response.context_data["rating_form"].fields)

    def test_not_logged_in_user_cant_rate(self):
        response = self.client.post(
            reverse("book-detail", kwargs={"pk": self.book1.pk}),
            {"rate": 5},
        )
        self.assertEqual(response.status_code, 403)

    def test_logged_in_user_can_rate(self):
        self.client.login(username="user1", password="password1")
        response = self.client.post(
            reverse("book-detail", kwargs={"pk": self.book1.pk}),
            {"rate": 5},
        )
        self.assertEqual(response.status_code, 200)
        self.book1 = Book.objects.get(pk=self.book1.pk)
        self.assertEqual(self.book1.average_rating, 5)
