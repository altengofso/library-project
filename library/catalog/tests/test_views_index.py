import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "library.settings")
django.setup()

from catalog.models import Author, Book, BookRating
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class IndexViewTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.users = [
            User.objects.create_user(
                username=f"user{i}",
                password=f"password{i}",
                email=f"user{i}@email.com",
            )
            for i in range(2)
        ]
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
                added_by=cls.users[0],
            )
            for i in range(12)
        ]
        for i in range(10):
            for j in range(2):
                BookRating.objects.create(
                    book=cls.books[i],
                    user=cls.users[j],
                    rate=5 if i == 0 else 4 if i == 1 else 1,
                )
        cls.rated_number = len(
            Book.objects.exclude(rating__isnull=True).distinct()
        )

    def test_url_accessible(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)

    def test_is_paginated(self):
        response = self.client.get(reverse("index"))
        self.assertTrue("is_paginated" in response.context_data)
        self.assertEqual(response.context_data["is_paginated"], True)
        self.assertEqual(len(response.context_data["object_list"]), 6)

    def test_lists_only_rated_books(self):
        response = self.client.get(reverse("index"))
        self.assertTrue("paginator" in response.context_data)
        self.assertEqual(
            response.context_data["paginator"].count, self.rated_number
        )
        self.assertEqual(
            response.context_data["paginator"].num_pages,
            self.rated_number // 6 + (0 if self.rated_number % 6 == 0 else 1),
        )

    def test_books_ordered_by_avgerage_rate(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(
            response.context_data["books"],
            sorted(
                response.context_data["books"],
                key=lambda book: book.average_rating,
                reverse=True,
            ),
        )
