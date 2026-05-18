from django.urls import include, path

urlpatterns = [
    path("auth/", include("registration.api.v1.urls")),
]
