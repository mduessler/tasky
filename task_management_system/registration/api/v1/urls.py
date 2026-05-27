from django.urls import path
from registration.api.v1.views import ActivateUserView, RegisterUserView

urlpatterns = [
    path("register/", RegisterUserView.as_view(), name="register-user"),
    path("activate/", ActivateUserView.as_view(), name="activate-user"),
]
