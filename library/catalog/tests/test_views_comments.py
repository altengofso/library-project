import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "library.settings")
django.setup()

from catalog.models import Author, Book, BookComment
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class BookCommentViewTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user1 = User.objects.create_user(
            username="user1",
            password="password1",
            email="user1@email.com",
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
            poster="posters/book1.jpg",
            added_by=cls.user1,
        )
        cls.book2 = Book.objects.create(
            title="Book 2",
            author=cls.author,
            summary="Lorem ipsum dolor sit amet",
            publication_year=2023,
            poster="posters/book2.jpg",
            added_by=cls.user2,
        )
        cls.comments1 = [
            BookComment.objects.create(
                user=cls.user1,
                book=cls.book1,
                content="content",
            )
            for _ in range(10)
        ]
        cls.comments2 = [
            BookComment.objects.create(
                user=cls.user2,
                book=cls.book2,
                content="content",
            )
            for _ in range(10)
        ]

    def test_is_paginated(self):
        response = self.client.get(
            reverse("book-detail", kwargs={"pk": self.book1.pk})
        )
        self.assertTrue("is_paginated" in response.context_data)
        self.assertEqual(response.context_data["is_paginated"], True)
        self.assertEqual(len(response.context_data["object_list"]), 6)

    def test_lists_all_comments_of_current_book(self):
        response = self.client.get(
            reverse("book-detail", kwargs={"pk": self.book1.pk})
        )
        self.assertTrue("paginator" in response.context_data)
        self.assertEqual(
            response.context_data["paginator"].count, len(self.comments1)
        )
        self.assertEqual(
            response.context_data["paginator"].num_pages,
            len(self.comments1) // 6
            + (0 if len(self.comments1) % 6 == 0 else 1),
        )

    def test_has_new_comment_form(self):
        response = self.client.get(
            reverse("book-detail", kwargs={"pk": self.book1.pk})
        )
        self.assertTrue("comment_form" in response.context_data)
        self.assertTrue(
            "content" in response.context_data["comment_form"].fields
        )

    def test_not_logged_in_user_cant_comment(self):
        response = self.client.post(
            reverse("book-detail", kwargs={"pk": self.book1.pk}),
            {"content": "content"},
        )
        self.assertEqual(response.status_code, 403)

    def test_logged_in_user_can_comment(self):
        self.client.login(username="user1", password="password1")
        response = self.client.post(
            reverse("book-detail", kwargs={"pk": self.book1.pk}),
            {"content": "content of last comment"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context_data["paginator"].count, len(self.comments1) + 1
        )
        self.assertEqual(
            response.context_data["object_list"][0].content,
            "content of last comment",
        )
        self.assertEqual(
            response.context_data["object_list"][0].user, self.user1
        )
        self.assertEqual(
            response.context_data["object_list"][0].book, self.book1
        )


class BookCommentDeleteViewTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user1 = User.objects.create_user(
            username="user1",
            password="password1",
            email="user1@email.com",
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
            title="Book ",
            author=cls.author,
            summary="Lorem ipsum dolor sit amet",
            publication_year=2023,
            poster="posters/book.jpg",
            added_by=cls.user1,
        )
        cls.comment1 = BookComment.objects.create(
            user=cls.user1,
            book=cls.book,
            content="content",
        )
        cls.comment2 = BookComment.objects.create(
            user=cls.user2,
            book=cls.book,
            content="content",
        )

    def test_url_unaccessible_for_not_logged_in_user(self):
        response = self.client.get(
            reverse(
                "bookcomment-delete",
                kwargs={"pk": self.comment1.pk, "book_id": self.book.pk},
            )
        )
        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('bookcomment-delete',kwargs={'pk': self.comment1.pk, 'book_id': self.book.pk})}",
        )

    def test_url_unaccessible_for_logged_in_user(self):
        self.client.login(username="user1", password="password1")
        response = self.client.get(
            reverse(
                "bookcomment-delete",
                kwargs={"pk": self.comment1.pk, "book_id": self.book.pk},
            )
        )
        self.assertEqual(response.status_code, 405)

    def test_url_successful_delete_submit(self):
        self.client.login(username="user1", password="password1")
        response = self.client.post(
            reverse(
                "bookcomment-delete",
                kwargs={"pk": self.comment1.pk, "book_id": self.book.pk},
            )
        )
        self.assertEqual(
            len(BookComment.objects.filter(pk=self.comment1.pk).all()), 0
        )
        self.assertRedirects(
            response, reverse("book-detail", kwargs={"pk": self.book.pk})
        )

    def test_url_unsuccessful_delete_submit_not_owner(self):
        self.client.login(username="user1", password="password1")
        response = self.client.post(
            reverse(
                "bookcomment-delete",
                kwargs={"pk": self.comment2.pk, "book_id": self.book.pk},
            )
        )
        self.assertEqual(
            len(BookComment.objects.filter(pk=self.comment2.pk).all()), 1
        )
        self.assertEqual(response.status_code, 403)
