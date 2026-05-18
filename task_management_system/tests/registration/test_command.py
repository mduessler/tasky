import pytest
from django.core.management import call_command
from django_celery_beat.models import IntervalSchedule, PeriodicTask


@pytest.mark.django_db
class TestCleanTokensCommand:
    def test_command_creates_schedule_and_task(self):
        call_command("clean_tokens")

        schedule = IntervalSchedule.objects.get(
            every=1,
            period=IntervalSchedule.MINUTES,
        )

        task = PeriodicTask.objects.get(
            name="Cleanup Expired Tokens",
            task="verification.tasks.cleanup_expired_tokens",
        )

        assert task.interval == schedule

    def test_command_is_idempotent(self):
        call_command("clean_tokens")
        call_command("clean_tokens")

        assert (
            IntervalSchedule.objects.filter(
                every=1,
                period=IntervalSchedule.MINUTES,
            ).count()
            == 1
        )

        assert (
            PeriodicTask.objects.filter(
                name="Cleanup Expired Tokens",
                task="verification.tasks.cleanup_expired_tokens",
            ).count()
            == 1
        )
