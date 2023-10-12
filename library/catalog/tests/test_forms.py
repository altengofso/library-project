import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "library.settings")
django.setup()

from catalog.forms import BookCommentForm, BookForm
from catalog.models import Author
from django.test import TestCase


class BookCommentFormTest(TestCase):
    def test_content_field_label(self):
        form = BookCommentForm()
        expected_label = "Содержание"
        self.assertEqual(form.fields["content"].label, expected_label)

    def test_content_field_max_length(self):
        data = {"content": "content" * 500}
        form = BookCommentForm(data=data)
        self.assertFalse(form.is_valid())

    def test_content_field_required(self):
        data = {}
        form = BookCommentForm(data=data)
        self.assertFalse(form.is_valid())


class BookFormTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.lorem_short = ("content" * 50)[:50]
        cls.lorem_long = "content" * 500
        cls.author = Author.objects.create(
            name="Author 1",
            date_of_birth="1990-01-01",
            bio=cls.lorem_short,
            photo="authors/photo.jpg",
        )

    def test_title_field_label(self):
        form = BookForm()
        expected_label = "Название"
        self.assertEqual(form.fields["title"].label, expected_label)

    def test_author_field_label(self):
        form = BookForm()
        expected_label = "Автор"
        self.assertEqual(form.fields["author"].label, expected_label)

    def test_summary_field_label(self):
        form = BookForm()
        expected_label = "Краткое описание"
        self.assertEqual(form.fields["summary"].label, expected_label)

    def test_publication_year_field_label(self):
        form = BookForm()
        expected_label = "Год издания"
        self.assertEqual(form.fields["publication_year"].label, expected_label)

    def test_poster_field_label(self):
        form = BookForm()
        expected_label = "Обложка"
        self.assertEqual(form.fields["poster"].label, expected_label)

    def test_poster_field_initial(self):
        form = BookForm()
        expected_initial = "posters/no-poster.jpg"
        self.assertEqual(form.fields["poster"].initial, expected_initial)

    def test_title_field_max_length(self):
        data = {
            "title": self.lorem_long,
            "author": self.author,
            "summary": self.lorem_short,
            "publication_year": 2023,
        }
        form = BookForm(data=data)
        self.assertFalse(form.is_valid())

    def test_title_field_required(self):
        data = {
            "author": self.author,
            "summary": self.lorem_short,
            "publication_year": 2023,
        }
        form = BookForm(data=data)
        self.assertFalse(form.is_valid())

    def test_author_field_required(self):
        data = {
            "title": self.lorem_short,
            "summary": self.lorem_short,
            "publication_year": 2023,
        }
        form = BookForm(data=data)
        self.assertFalse(form.is_valid())

    def test_summary_field_max_length(self):
        data = {
            "title": self.lorem_short,
            "author": self.author,
            "summary": self.lorem_long,
            "publication_year": 2023,
        }
        form = BookForm(data=data)
        self.assertFalse(form.is_valid())

    def test_summary_field_required(self):
        data = {
            "title": self.lorem_short,
            "author": self.author,
            "publication_year": 2023,
        }
        form = BookForm(data=data)
        self.assertFalse(form.is_valid())

    def test_publication_year_field_gte_0(self):
        data = {
            "title": self.lorem_short,
            "author": self.author,
            "summary": self.lorem_short,
            "publication_year": -1,
        }
        form = BookForm(data=data)
        self.assertFalse(form.is_valid())

    def test_publication_year_field_lte_2999(self):
        data = {
            "title": self.lorem_short,
            "author": self.author,
            "summary": self.lorem_short,
            "publication_year": 3000,
        }
        form = BookForm(data=data)
        self.assertFalse(form.is_valid())

    def test_publication_year_field_required(self):
        data = {
            "title": self.lorem_short,
            "author": self.author,
            "summary": self.lorem_short,
        }
        form = BookForm(data=data)
        self.assertFalse(form.is_valid())
