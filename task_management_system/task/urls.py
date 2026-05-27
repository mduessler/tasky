from django.urls import include, path

urlpatterns = [
    path("v1/", include("task.api.v1.urls")),
]
