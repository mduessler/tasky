from django.urls import include, path

urlpatterns = [
    path("v1/", include("user.api.v1.urls")),
]
