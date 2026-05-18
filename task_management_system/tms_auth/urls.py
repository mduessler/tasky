from django.urls import include, path

urlpatterns = [
    path("auth/", include("tms_auth.api.v1.urls")),
]
