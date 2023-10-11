from typing import Any

from catalog.models import Book
from django.contrib.auth import authenticate, login, views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.query import QuerySet
from django.forms import Form
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views import generic

from .forms import RegisterForm
from .models import User


class AccountLoginView(views.LoginView):
    redirect_authenticated_user = True


class AccountProfileView(LoginRequiredMixin, generic.ListView):
    model = Book
    context_object_name = "books"
    template_name = "profile.html"
    paginate_by = 6

    def get_queryset(self) -> QuerySet[Any]:
        return Book.objects.filter(added_by=self.request.user)


class RegisterUser(generic.FormView):
    template_name = "register.html"
    form_class = RegisterForm

    def get_success_url(self) -> str:
        return reverse("index")

    def dispatch(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponse:
        if self.request.user.is_authenticated:
            return HttpResponseRedirect(self.success_url)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form: Form) -> HttpResponse:
        username = form.cleaned_data["username"].lower()
        email = form.cleaned_data["email"]
        password = form.cleaned_data["password1"]
        User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )
        user = authenticate(username=username, password=password)
        login(self.request, user)
        return super().form_valid(form)
