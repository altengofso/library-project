from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.db.models.query import QuerySet
from django.forms.models import BaseModelForm
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseForbidden,
    HttpResponseNotAllowed,
)
from django.urls import reverse
from django.views import generic
from django.views.generic.list import MultipleObjectMixin
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination

from .forms import BookCommentForm, BookForm, BookRatingForm
from .models import Author, Book, BookComment
from .serializers import BookSerializer


class IndexView(generic.ListView):
    context_object_name = "books"
    paginate_by = 6
    template_name = "index.html"

    def get_queryset(self) -> QuerySet[Any]:
        return sorted(
            Book.objects.exclude(rating__isnull=True).distinct(),
            key=lambda book: book.average_rating,
            reverse=True,
        )


class SearchView(generic.ListView):
    context_object_name = "books"
    paginate_by = 6
    template_name = "search.html"

    def get_queryset(self) -> QuerySet[Any]:
        query = self.request.GET.get("q")
        if query:
            return Book.objects.filter(
                Q(title__icontains=query) | Q(author__name__icontains=query)
            )
        return Book.objects.none()


class BookListView(generic.ListView):
    model = Book
    context_object_name = "books"
    paginate_by = 6


class BookDetailView(generic.DetailView, MultipleObjectMixin):
    model = Book
    paginate_by = 6

    def get_success_url(self) -> str:
        return reverse("book-detail", kwargs={"pk": self.object.pk})

    def get(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponse:
        return self.render_to_response(context=self.get_context_data(**kwargs))

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        self.object = self.get_object()
        object_list = BookComment.objects.filter(book=self.object)
        context = super().get_context_data(object_list=object_list, **kwargs)
        context["comment_form"] = BookCommentForm()
        context["rating_form"] = BookRatingForm()
        return context

    def post(
        self, request: HttpRequest, *args: str, **kwargs: Any
    ) -> HttpResponse:
        if not request.user.is_authenticated:
            return HttpResponseForbidden()
        self.object = self.get_object()
        comment_form = BookCommentForm(request.POST)
        rating_form = BookRatingForm(request.POST)
        if comment_form.is_valid():
            comment_form.instance.user = self.request.user
            comment_form.instance.book = self.object
            comment_form.save()
            return self.render_to_response(
                context=self.get_context_data(**kwargs)
            )
        elif rating_form.is_valid():
            rating_form.instance.user = self.request.user
            rating_form.instance.book = self.object
            rating_form.save()
            return self.render_to_response(
                context=self.get_context_data(**kwargs)
            )
        else:
            context = self.get_context_data(**kwargs)
            context["comment_form"] = comment_form
            context["rating_form"] = rating_form
            return self.render_to_response(context=context)


class BookCreateView(LoginRequiredMixin, generic.CreateView):
    model = Book
    form_class = BookForm

    def get_success_url(self) -> str:
        return reverse("book-detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        form.instance.added_by = self.request.user
        form.save()
        return super().form_valid(form)


class BookUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Book
    form_class = BookForm

    def get_success_url(self) -> str:
        return reverse("book-detail", kwargs={"pk": self.object.pk})

    def post(
        self, request: HttpRequest, *args: str, **kwargs: Any
    ) -> HttpResponse:
        book = self.get_object()
        if book.added_by != self.request.user:
            return HttpResponseForbidden()
        return super().post(request, *args, **kwargs)


class BookDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Book

    def get_success_url(self) -> str:
        return reverse("profile")

    def get(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponse:
        return HttpResponseNotAllowed(permitted_methods=["POST"])

    def post(
        self, request: HttpRequest, *args: str, **kwargs: Any
    ) -> HttpResponse:
        book = self.get_object()
        if book.added_by != self.request.user:
            return HttpResponseForbidden()
        return super().post(request, *args, **kwargs)


class BookCommentDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = BookComment

    def get_success_url(self) -> str:
        return reverse("book-detail", kwargs={"pk": self.kwargs["book_id"]})

    def get(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponse:
        return HttpResponseNotAllowed(permitted_methods=["POST"])

    def post(
        self, request: HttpRequest, *args: str, **kwargs: Any
    ) -> HttpResponse:
        comment = self.get_object()
        if comment.user != self.request.user:
            return HttpResponseForbidden()
        return super().post(request, *args, **kwargs)


class AuthorListView(generic.ListView):
    model = Author
    context_object_name = "authors"
    paginate_by = 6


class AuthorDetailView(generic.DetailView, MultipleObjectMixin):
    model = Author
    context_object_name = "author"
    paginate_by = 6

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        object_list = Book.objects.filter(author=self.object)
        return super().get_context_data(object_list=object_list, **kwargs)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = "page_size"
    max_page_size = 20


class BooksListAPIView(generics.ListAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    pagination_class = StandardResultsSetPagination


class BooksRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
