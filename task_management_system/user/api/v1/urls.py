from rest_framework.routers import DefaultRouter
from user.api.v1.views import TmsUserView

router = DefaultRouter()
router.register(r"user", TmsUserView, basename="user")

urlpatterns = router.urls
