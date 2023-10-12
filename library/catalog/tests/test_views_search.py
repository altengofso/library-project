import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "library.settings")
django.setup()

from catalog.models import Author, Book
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class SearchViewTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create_user(
            username="user",
            password="password",
            email="user@email.com",
        )
        cls.author1 = Author.objects.create(
            name="Author 1",
            date_of_birth="1990-01-01",
            bio="Lorem ipsum dolor sit amet",
            photo="authors/photo.jpg",
        )
        cls.author2 = Author.objects.create(
            name="Author 2",
            date_of_birth="1990-01-01",
            bio="Lorem ipsum dolor sit amet",
            photo="authors/photo.jpg",
        )
        cls.books = [
            Book.objects.create(
                title="Even" if (i % 2 == 0) else "Odd",
                author=cls.author1 if (i % 2 == 0) else cls.author2,
                summary="Lorem ipsum dolor sit amet",
                publication_year=2023,
                poster=f"posters/book{i}.jpg",
                added_by=cls.user,
            )
            for i in range(24)
        ]
        cls.even_books_number = len(Book.objects.filter(title="Even"))
        cls.odd_books_number = len(Book.objects.filter(title="Odd"))
        cls.author1_books_number = len(Book.objects.filter(author=cls.author1))
        cls.author2_books_number = len(Book.objects.filter(author=cls.author2))

    def test_url_accessible(self):
        response = self.client.get(reverse("search"))
        self.assertEqual(response.status_code, 200)

    def test_is_paginated(self):
        response = self.client.get(reverse("search"), {"q": "even"})
        self.assertTrue("is_paginated" in response.context_data)
        self.assertEqual(response.context_data["is_paginated"], True)
        self.assertEqual(len(response.context_data["object_list"]), 6)

    def test_searchable_by_book_title(self):
        response = self.client.get(reverse("search"), {"q": "odd"})
        self.assertTrue("paginator" in response.context_data)
        self.assertEqual(
            response.context_data["paginator"].count, self.odd_books_number
        )
        self.assertEqual(
            response.context_data["paginator"].num_pages,
            self.odd_books_number // 6
            + (0 if self.odd_books_number % 6 == 0 else 1),
        )

    def test_searchable_by_author_name(self):
        response = self.client.get(reverse("search"), {"q": self.author1.name})
        self.assertTrue("paginator" in response.context_data)
        self.assertEqual(
            response.context_data["paginator"].count, self.odd_books_number
        )
        self.assertEqual(
            response.context_data["paginator"].num_pages,
            self.odd_books_number // 6
            + (0 if self.odd_books_number % 6 == 0 else 1),
        )
