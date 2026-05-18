from django.urls import path
from tms_auth.api.v1.views import JwtLogoutView, JwtRefreshView, JwtTokenObtainPairView

urlpatterns = [
    path("login/", JwtTokenObtainPairView.as_view(), name="login-jwt"),
    path("refresh/", JwtRefreshView.as_view(), name="refresh-jwt"),
    path("logout/", JwtLogoutView.as_view(), name="logout-jwt"),
]
