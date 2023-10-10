from django.urls import path

from . import views

urlpatterns = [
    path("", view=views.IndexView.as_view(), name="index"),
    path("search", view=views.SearchView.as_view(), name="search"),
    path("books/", view=views.BookListView.as_view(), name="books"),
    path(
        "books/create/",
        view=views.BookCreateView.as_view(),
        name="book-create",
    ),
    path(
        "books/<pk>/",
        view=views.BookDetailView.as_view(),
        name="book-detail",
    ),
    path(
        "books/<pk>/update",
        view=views.BookUpdateView.as_view(),
        name="book-update",
    ),
    path(
        "books/<pk>/delete",
        view=views.BookDeleteView.as_view(),
        name="book-delete",
    ),
    path(
        "books/<book_id>/comment/<pk>/delete",
        view=views.BookCommentDeleteView.as_view(),
        name="bookcomment-delete",
    ),
    path("authors/", view=views.AuthorListView.as_view(), name="authors"),
    path(
        "authors/<pk>/",
        view=views.AuthorDetailView.as_view(),
        name="author-detail",
    ),
]
