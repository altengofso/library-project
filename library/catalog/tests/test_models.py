import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "library.settings")
django.setup()

from datetime import datetime

from catalog.models import Author, Book, BookComment, BookRating
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class AuthorModelTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.author = Author.objects.create(
            name="Author 1",
            date_of_birth="1990-01-01",
            bio="Lorem ipsum dolor sit amet",
            photo="authors/photo.jpg",
        )
        cls.author_default_photo = Author.objects.create(
            name="Author 2",
            date_of_birth="1990-01-01",
            bio="Lorem ipsum dolor sit amet",
        )

    def test_get_absolute_url(self):
        expected_url = reverse("author-detail", args=[str(self.author.id)])
        self.assertEqual(self.author.get_absolute_url(), expected_url)

    def test_str_representation(self):
        self.assertEqual(str(self.author), "Author 1")

    def test_bio_short(self):
        expected_bio_short = "Lorem ipsum dolor sit amet..."
        self.assertEqual(self.author.bio_short(), expected_bio_short)

    def test_preview(self):
        expected_preview = (
            "<img src='/media/authors/photo.jpg' style='max-height: 200px;'>"
        )
        self.assertEqual(self.author.preview(), expected_preview)

    def test_photo_default_url(self):
        expected_photo_url = "/media/authors/no-photo.webp"
        self.assertEqual(
            self.author_default_photo.photo.url, expected_photo_url
        )


class BookModelTestCase(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.author = Author.objects.create(
            name="Author 1",
            date_of_birth="1990-01-01",
            bio="Lorem ipsum dolor sit amet",
            photo="authors/photo.jpg",
        )
        cls.user = User.objects.create_user(
            username="user1",
            password="password1",
            email="user1@email.com",
        )
        cls.book = Book.objects.create(
            title="Book 1",
            author=cls.author,
            summary="Lorem ipsum dolor sit amet",
            publication_year=2021,
            poster="posters/book1.jpg",
            added_by=cls.user,
        )
        cls.book_default_poster = Book.objects.create(
            title="Book 2",
            author=cls.author,
            summary="Lorem ipsum dolor sit amet",
            publication_year=2021,
            added_by=cls.user,
        )

    def test_get_absolute_url(self):
        expected_url = reverse("book-detail", args=[str(self.book.id)])
        self.assertEqual(self.book.get_absolute_url(), expected_url)

    def test_str_representation(self):
        self.assertEqual(str(self.book), "Book 1")

    def test_summary_short(self):
        expected_summary_short = "Lorem ipsum dolor sit amet..."
        self.assertEqual(self.book.summary_short(), expected_summary_short)

    def test_preview(self):
        expected_preview = (
            "<img src='/media/posters/book1.jpg' style='max-height: 200px;'>"
        )
        self.assertEqual(self.book.preview(), expected_preview)

    def test_average_rating(self):
        BookRating.objects.create(
            rate=4, book=self.book, user=self.book.added_by
        )
        BookRating.objects.create(
            rate=5,
            book=self.book,
            user=User.objects.create_user(
                username="user2",
                password="password2",
                email="user2@email.com",
            ),
        )
        expected_average_rating = 4.5
        self.assertEqual(self.book.average_rating, expected_average_rating)

    def test_poster_default_url(self):
        expected_poster_url = "/media/posters/no-poster.jpg"
        self.assertEqual(
            self.book_default_poster.poster.url, expected_poster_url
        )

    def test_publication_year_gte_0(self):
        with self.assertRaises(IntegrityError):
            Book.objects.create(
                title="Book 3",
                author=self.author,
                summary="Lorem ipsum dolor sit amet",
                publication_year=-1,
                poster="posters/book3.jpg",
                added_by=self.user,
            )

    def test_publication_year_lte_2999(self):
        with self.assertRaises(IntegrityError):
            Book.objects.create(
                title="Book 4",
                author=self.author,
                summary="Lorem ipsum dolor sit amet",
                publication_year=3000,
                poster="posters/book4.jpg",
                added_by=self.user,
            )


class BookCommentModelTestCase(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.author = Author.objects.create(
            name="Author 1",
            date_of_birth="1990-01-01",
            bio="Lorem ipsum dolor sit amet",
            photo="authors/photo.jpg",
        )
        cls.book = Book.objects.create(
            title="Book 1",
            author=cls.author,
            summary="Lorem ipsum dolor sit amet",
            publication_year=2021,
            poster="posters/sample.jpg",
            added_by=User.objects.create_user(
                username="user1",
                password="password1",
                email="user1@email.com",
            ),
        )
        cls.user = User.objects.create_user(
            username="user2",
            password="password2",
            email="user2@email.com",
        )
        cls.comment = BookComment.objects.create(
            user=cls.user,
            book=cls.book,
            content="Great book!",
        )

    def test_str_representation(self):
        expected_str = f"Комментарий пользователя {self.user.username} на книгу {self.book.title}"
        self.assertEqual(str(self.comment), expected_str)

    def test_created_at_auto_added_type(self):
        self.assertEqual(type(self.comment.created_at), datetime)


class BookRatingModelTestCase(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.author = Author.objects.create(
            name="Author 1",
            date_of_birth="1990-01-01",
            bio="Lorem ipsum dolor sit amet",
            photo="authors/photo.jpg",
        )
        cls.book = Book.objects.create(
            title="Book 1",
            author=cls.author,
            summary="Lorem ipsum dolor sit amet",
            publication_year=2021,
            poster="posters/sample.jpg",
            added_by=User.objects.create_user(
                username="user1",
                password="password1",
                email="user1@email.com",
            ),
        )
        cls.user = User.objects.create_user(
            username="user2",
            password="password2",
            email="user2@email.com",
        )
        cls.rating = BookRating.objects.create(
            rate=5,
            book=cls.book,
            user=cls.user,
        )

    def test_str_representation(self):
        expected_str = f"Оценка пользователя {self.user.username} на книгу {self.book.title}"
        self.assertEqual(str(self.rating), expected_str)

    def test_save_method(self):
        existing_rating = self.rating
        existing_rating.rate = 4
        existing_rating.save()
        updated_rating = BookRating.objects.get(book=self.book, user=self.user)
        self.assertEqual(updated_rating.rate, 4)
