from django import forms

from .models import Book, BookComment, BookRating


class BookCommentForm(forms.ModelForm):
    class Meta:
        model = BookComment
        fields = ["content"]


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ["title", "author", "summary", "publication_year", "poster"]


class BookRatingForm(forms.ModelForm):
    class Meta:
        model = BookRating
        fields = ["rate"]
