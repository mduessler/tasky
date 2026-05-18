from typing import Any

from django.core.management.base import BaseCommand
from django_celery_beat.models import IntervalSchedule, PeriodicTask


class Command(BaseCommand):  # type: ignore[misc]
    def handle(self, *args: Any, **options: Any) -> str | None:
        schedule, _ = IntervalSchedule.objects.get_or_create(
            every=1, period=IntervalSchedule.MINUTES
        )

        PeriodicTask.objects.get_or_create(
            interval=schedule,
            name="Cleanup Expired Tokens",
            task="verification.tasks.cleanup_expired_tokens",
        )
        return None
