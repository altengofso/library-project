from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.forms.models import BaseModelForm
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseForbidden,
    HttpResponseNotAllowed,
)
from django.urls import reverse
from django.views import generic
from django.views.generic.edit import FormMixin
from django.views.generic.list import MultipleObjectMixin

from .forms import BookCommentForm, BookForm
from .models import Author, Book, BookComment


class IndexView(generic.TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["books"] = Book.objects.annotate(
            num_comments=Count("comments")
        ).order_by("-num_comments")[:6]
        return context


class SearchView(generic.TemplateView, MultipleObjectMixin):
    context_object_name = "books"
    paginate_by = 6
    template_name = "search.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        object_list = []
        query = self.request.GET.get("q")
        if query:
            object_list = Book.objects.filter(
                Q(title__icontains=query) | Q(author__name__icontains=query)
            )
        context = super().get_context_data(object_list=object_list, **kwargs)
        return context


class BookListView(generic.ListView):
    model = Book
    context_object_name = "books"
    paginate_by = 6


class BookDetailView(generic.DetailView, FormMixin, MultipleObjectMixin):
    model = Book
    paginate_by = 6
    form_class = BookCommentForm

    def get_success_url(self) -> str:
        return reverse("book-detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        object_list = BookComment.objects.filter(book=self.object)
        context = super().get_context_data(object_list=object_list, **kwargs)
        return context

    def post(
        self, request: HttpRequest, *args: str, **kwargs: Any
    ) -> HttpResponse:
        if not request.user.is_authenticated:
            return HttpResponseForbidden()
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        form.instance.user = self.request.user
        form.instance.book = self.object
        form.save()
        return super().form_valid(form)


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
