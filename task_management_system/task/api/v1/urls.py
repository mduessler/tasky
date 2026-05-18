from rest_framework.routers import DefaultRouter
from task.api.v1.views import (
    TaskMembershipViewSet,
    TaskNoteViewSet,
    TaskViewSet,
)

router = DefaultRouter()
router.register(r"task", TaskViewSet, basename="task")
router.register(r"membership", TaskMembershipViewSet, basename="membership")
router.register(r"note", TaskNoteViewSet, basename="note")

urlpatterns = router.urls
