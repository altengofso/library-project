from django.urls import include, path

from . import views

urlpatterns = [
    path("login/", view=views.AccountLoginView.as_view(), name="login"),
    path("profile/", view=views.AccountProfileView.as_view(), name="profile"),
    path(
        "register/",
        view=views.RegisterUser.as_view(),
        name="register",
    ),
    path("", include("django.contrib.auth.urls")),
]
