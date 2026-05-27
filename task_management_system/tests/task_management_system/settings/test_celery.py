from task_management_system.settings import production


class TestCeleryConfiguration:
    def test_celery_beat_schedule_structure(self):
        expected = {
            "cleanup-tokens-every-minute": {
                "task": "registration.tasks.cleanup_expired_tokens",
                "schedule": 60.0,
            },
        }

        for key, value in expected.items():
            assert key in production.CELERY_BEAT_SCHEDULE
            assert value == production.CELERY_BEAT_SCHEDULE[key]

    def test_celery_beat_sync_every(self):
        assert production.CELERY_BEAT_SYNC_EVERY == 1
