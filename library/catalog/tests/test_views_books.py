import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "library.settings")
django.setup()

from catalog.models import Author, Book
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class BookListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create_user(
            username="user",
            password="password",
            email="user@email.com",
        )
        cls.author = Author.objects.create(
            name="Author",
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
        cls.books_number = len(Book.objects.all())

    def test_url_accessible(self):
        response = self.client.get(reverse("books"))
        self.assertEqual(response.status_code, 200)

    def test_is_paginated(self):
        response = self.client.get(reverse("books"))
        self.assertTrue("is_paginated" in response.context_data)
        self.assertEqual(response.context_data["is_paginated"], True)
        self.assertEqual(len(response.context_data["object_list"]), 6)

    def test_lists_all_books(self):
        response = self.client.get(reverse("books"))
        self.assertTrue("paginator" in response.context_data)
        self.assertEqual(
            response.context_data["paginator"].count, self.books_number
        )
        self.assertEqual(
            response.context_data["paginator"].num_pages,
            self.books_number // 6 + (0 if self.books_number % 6 == 0 else 1),
        )


class BookDetailViewTest(TestCase):
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

    def test_url_accessible(self):
        response = self.client.get(
            reverse("book-detail", kwargs={"pk": self.book1.pk})
        )
        self.assertEqual(response.status_code, 200)


class BookCreateViewTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create_user(
            username="user",
            password="password",
            email="user@email.com",
        )
        cls.author = Author.objects.create(
            name="Author",
            date_of_birth="1990-01-01",
            bio="Lorem ipsum dolor sit amet",
            photo="authors/photo.jpg",
        )

    def test_url_unaccessible_for_not_logged_in_user(self):
        response = self.client.get(reverse("book-create"))
        self.assertRedirects(
            response, f"{reverse('login')}?next={reverse('book-create')}"
        )

    def test_url_accessible_for_logged_in_user(self):
        self.client.login(username="user", password="password")
        response = self.client.get(reverse("book-create"))
        self.assertEqual(response.status_code, 200)

    def test_has_new_book_form(self):
        self.client.login(username="user", password="password")
        response = self.client.get(reverse("book-create"))
        self.assertTrue("form" in response.context_data)
        self.assertTrue("title" in response.context_data["form"].fields)
        self.assertTrue("author" in response.context_data["form"].fields)
        self.assertTrue("summary" in response.context_data["form"].fields)
        self.assertTrue(
            "publication_year" in response.context_data["form"].fields
        )
        self.assertTrue("poster" in response.context_data["form"].fields)

    def test_successful_new_book_form_submit(self):
        self.client.login(username="user", password="password")
        response = self.client.post(
            reverse("book-create"),
            {
                "title": "test_successful_new_book_form_submit",
                "author": self.author.pk,
                "summary": "summary",
                "publication_year": 2023,
            },
        )
        book = Book.objects.filter(
            title="test_successful_new_book_form_submit"
        ).first()
        self.assertRedirects(
            response, reverse("book-detail", kwargs={"pk": book.pk})
        )
        self.assertEqual(book.added_by, self.user)
        self.assertEqual(book.author, self.author)
        self.assertEqual(book.summary, "summary")
        self.assertEqual(book.publication_year, 2023)

    def test_unsuccessful_new_book_form_submit_not_logged(self):
        response = self.client.post(
            reverse("book-create"),
            {
                "title": "test_successful_new_book_form_submit",
                "author": self.author.pk,
                "summary": "summary",
                "publication_year": 2023,
            },
        )
        self.assertRedirects(
            response, f"{reverse('login')}?next={reverse('book-create')}"
        )

    def test_unsuccessful_new_book_form_submit_title_missing(self):
        self.client.login(username="user", password="password")
        response = self.client.post(
            reverse("book-create"),
            {
                "author": self.author.pk,
                "summary": "summary",
                "publication_year": 2023,
            },
        )
        self.assertTrue("title" in response.context_data["form"].errors)

    def test_unsuccessful_new_book_form_submit_title_too_long(self):
        self.client.login(username="user", password="password")
        response = self.client.post(
            reverse("book-create"),
            {
                "title": "title" * 100,
                "author": self.author.pk,
                "summary": "summary",
                "publication_year": 2023,
            },
        )
        self.assertTrue("title" in response.context_data["form"].errors)

    def test_unsuccessful_new_book_form_submit_author_missing(self):
        self.client.login(username="user", password="password")
        response = self.client.post(
            reverse("book-create"),
            {
                "title": "title",
                "summary": "summary",
                "publication_year": 2023,
            },
        )
        self.assertTrue("author" in response.context_data["form"].errors)

    def test_unsuccessful_new_book_form_submit_author_wrong(self):
        self.client.login(username="user", password="password")
        response = self.client.post(
            reverse("book-create"),
            {
                "title": "title",
                "author": 123,
                "summary": "summary",
                "publication_year": 2023,
            },
        )
        self.assertTrue("author" in response.context_data["form"].errors)

    def test_unsuccessful_new_book_form_submit_summary_missing(self):
        self.client.login(username="user", password="password")
        response = self.client.post(
            reverse("book-create"),
            {
                "title": "title",
                "author": self.author.pk,
                "publication_year": 2023,
            },
        )
        self.assertTrue("summary" in response.context_data["form"].errors)

    def test_unsuccessful_new_book_form_submit_summary_too_long(self):
        self.client.login(username="user", password="password")
        response = self.client.post(
            reverse("book-create"),
            {
                "title": "title",
                "author": self.author.pk,
                "summary": "summary" * 1000,
                "publication_year": 2023,
            },
        )
        self.assertTrue("summary" in response.context_data["form"].errors)

    def test_unsuccessful_new_book_form_submit_publication_year_missing(self):
        self.client.login(username="user", password="password")
        response = self.client.post(
            reverse("book-create"),
            {
                "title": "title",
                "author": self.author.pk,
                "summary": "summary" * 1000,
            },
        )
        self.assertTrue(
            "publication_year" in response.context_data["form"].errors
        )

    def test_unsuccessful_new_book_form_submit_publication_year_wrong(self):
        self.client.login(username="user", password="password")
        response = self.client.post(
            reverse("book-create"),
            {
                "title": "title",
                "author": self.author.pk,
                "summary": "summary",
                "publication_year": -1,
            },
        )
        self.assertTrue(
            "publication_year" in response.context_data["form"].errors
        )
        response = self.client.post(
            reverse("book-create"),
            {
                "title": "title",
                "author": self.author.pk,
                "summary": "summary",
                "publication_year": 3000,
            },
        )
        self.assertTrue("__all__" in response.context_data["form"].errors)


class BookUpdateViewTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create_user(
            username="user",
            password="password",
            email="user@email.com",
        )
        cls.user2 = User.objects.create_user(
            username="user2",
            password="password2",
            email="user2@email.com",
        )
        cls.author = Author.objects.create(
            name="Author",
            date_of_birth="1990-01-01",
            bio="Lorem ipsum dolor sit amet",
            photo="authors/photo.jpg",
        )
        cls.book = Book.objects.create(
            title="Book",
            author=cls.author,
            summary="Lorem ipsum dolor sit amet",
            publication_year=2023,
            poster="posters/book.jpg",
            added_by=cls.user,
        )

    def test_url_unaccessible_for_not_logged_in_user(self):
        response = self.client.get(
            reverse("book-update", kwargs={"pk": self.book.pk})
        )
        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('book-update', kwargs={'pk': self.book.pk})}",
        )

    def test_url_accessible_for_logged_in_user(self):
        self.client.login(username="user", password="password")
        response = self.client.get(
            reverse("book-update", kwargs={"pk": self.book.pk})
        )
        self.assertEqual(response.status_code, 200)

    def test_has_update_book_form(self):
        self.client.login(username="user", password="password")
        response = self.client.get(
            reverse("book-update", kwargs={"pk": self.book.pk})
        )
        self.assertTrue("form" in response.context_data)
        self.assertTrue("title" in response.context_data["form"].fields)
        self.assertTrue("author" in response.context_data["form"].fields)
        self.assertTrue("summary" in response.context_data["form"].fields)
        self.assertTrue(
            "publication_year" in response.context_data["form"].fields
        )
        self.assertTrue("poster" in response.context_data["form"].fields)

    def test_successful_update_book_form_submit(self):
        self.client.login(username="user", password="password")
        response = self.client.post(
            reverse("book-update", kwargs={"pk": self.book.pk}),
            {
                "title": "test_successful_update_book_form_submit",
                "author": self.author.pk,
                "summary": "summary",
                "publication_year": 2023,
            },
        )
        book = Book.objects.filter(
            title="test_successful_update_book_form_submit"
        ).first()
        self.assertRedirects(
            response, reverse("book-detail", kwargs={"pk": book.pk})
        )
        self.assertEqual(book.added_by, self.user)
        self.assertEqual(book.author, self.author)
        self.assertEqual(book.summary, "summary")
        self.assertEqual(book.publication_year, 2023)

    def test_unsuccessful_update_book_form_submit_not_logged(self):
        response = self.client.post(
            reverse("book-update", kwargs={"pk": self.book.pk}),
            {
                "title": "test_successful_new_book_form_submit",
                "author": self.author.pk,
                "summary": "summary",
                "publication_year": 2023,
            },
        )
        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('book-update', kwargs={'pk': self.book.pk})}",
        )

    def test_unsuccessful_update_book_form_submit_not_owner(self):
        self.client.login(username="user2", password="password2")
        response = self.client.post(
            reverse("book-update", kwargs={"pk": self.book.pk}),
            {
                "title": "test_successful_new_book_form_submit",
                "author": self.author.pk,
                "summary": "summary",
                "publication_year": 2023,
            },
        )
        self.assertEqual(response.status_code, 403)


class BookDeleteViewTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create_user(
            username="user",
            password="password",
            email="user@email.com",
        )
        cls.user2 = User.objects.create_user(
            username="user2",
            password="password2",
            email="user2@email.com",
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
            poster="posters/book.jpg",
            added_by=cls.user,
        )
        cls.book2 = Book.objects.create(
            title="Book 2",
            author=cls.author,
            summary="Lorem ipsum dolor sit amet",
            publication_year=2023,
            poster="posters/book.jpg",
            added_by=cls.user2,
        )

    def test_url_unaccessible_for_not_logged_in_user(self):
        response = self.client.get(
            reverse("book-delete", kwargs={"pk": self.book1.pk})
        )
        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('book-delete', kwargs={'pk': self.book1.pk})}",
        )

    def test_url_unaccessible_for_logged_in_user(self):
        self.client.login(username="user", password="password")
        response = self.client.get(
            reverse("book-delete", kwargs={"pk": self.book1.pk})
        )
        self.assertEqual(response.status_code, 405)

    def test_successful_delete_book_form_submit(self):
        self.client.login(username="user", password="password")
        response = self.client.post(
            reverse("book-delete", kwargs={"pk": self.book1.pk}),
        )
        self.assertEqual(len(Book.objects.filter(pk=self.book1.pk).all()), 0)
        self.assertRedirects(response, reverse("profile"))

    def test_unsuccessful_delete_book_form_submit_not_logged_in(self):
        response = self.client.post(
            reverse("book-delete", kwargs={"pk": self.book2.pk}),
        )
        self.assertEqual(len(Book.objects.filter(pk=self.book2.pk).all()), 1)
        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('book-delete', kwargs={'pk': self.book2.pk})}",
        )

    def test_unsuccessful_delete_book_form_submit_not_owner(self):
        self.client.login(username="user", password="password")
        response = self.client.post(
            reverse("book-delete", kwargs={"pk": self.book2.pk}),
        )
        self.assertEqual(len(Book.objects.filter(pk=self.book2.pk).all()), 1)
        self.assertEqual(response.status_code, 403)
