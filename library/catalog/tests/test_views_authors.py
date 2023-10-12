import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "library.settings")
django.setup()

from catalog.models import Author, Book
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class AuthorListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.authors = [
            Author.objects.create(
                name=f"Author {i}",
                date_of_birth="1990-01-01",
                bio="Lorem ipsum dolor sit amet",
                photo="authors/photo.jpg",
            )
            for i in range(15)
        ]
        cls.authors_number = len(Author.objects.all())

    def test_url_accessible(self):
        response = self.client.get(reverse("authors"))
        self.assertEqual(response.status_code, 200)

    def test_is_paginated(self):
        response = self.client.get(reverse("authors"))
        self.assertTrue("is_paginated" in response.context_data)
        self.assertEqual(response.context_data["is_paginated"], True)
        self.assertEqual(len(response.context_data["object_list"]), 6)

    def test_lists_all_authors(self):
        response = self.client.get(reverse("authors"))
        self.assertTrue("paginator" in response.context_data)
        self.assertEqual(
            response.context_data["paginator"].count, self.authors_number
        )
        self.assertEqual(
            response.context_data["paginator"].num_pages,
            self.authors_number // 6
            + (0 if self.authors_number % 6 == 0 else 1),
        )


class AuthorDetailViewTest(TestCase):
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
        cls.books1 = [
            Book.objects.create(
                title=f"Book {i}",
                author=cls.author1,
                summary="Lorem ipsum dolor sit amet",
                publication_year=2023,
                poster=f"posters/book{i}.jpg",
                added_by=cls.user,
            )
            for i in range(15)
        ]
        cls.books2 = [
            Book.objects.create(
                title=f"Book {i}",
                author=cls.author2,
                summary="Lorem ipsum dolor sit amet",
                publication_year=2023,
                poster=f"posters/book{i}.jpg",
                added_by=cls.user,
            )
            for i in range(5)
        ]
        cls.books1_number = len(Book.objects.filter(author=cls.author1).all())

    def test_url_accesssible(self):
        response = self.client.get(
            reverse("author-detail", kwargs={"pk": self.author1.pk})
        )
        self.assertEqual(response.status_code, 200)

    def test_is_paginated(self):
        response = self.client.get(
            reverse("author-detail", kwargs={"pk": self.author1.pk})
        )
        self.assertTrue("is_paginated" in response.context_data)
        self.assertEqual(response.context_data["is_paginated"], True)
        self.assertEqual(len(response.context_data["object_list"]), 6)

    def test_lists_all_authors(self):
        response = self.client.get(
            reverse("author-detail", kwargs={"pk": self.author1.pk})
        )
        self.assertTrue("paginator" in response.context_data)
        self.assertEqual(
            response.context_data["paginator"].count, self.books1_number
        )
        self.assertEqual(
            response.context_data["paginator"].num_pages,
            self.books1_number // 6
            + (0 if self.books1_number % 6 == 0 else 1),
        )
