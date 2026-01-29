from django.urls import include, path

pathpatterns = [
    path("login/", include("accounts.urls")),
]