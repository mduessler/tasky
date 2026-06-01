import time

import pytest
from django.core.cache import cache
from user.models import TmsUser


@pytest.mark.django_db
class TestValidAuthrentication:
    def test_valid_email_and_password_returns_user(self, backend, active_user, active_user_data):
        result = backend.authenticate(
            None, email=active_user.email, password=active_user_data["password"]
        )

        assert isinstance(result, TmsUser)
        assert result.id == active_user.id

    def test_email_lookup_is_case_insensitive(self, backend, active_user, active_user_data):
        result = backend.authenticate(
            None, email=active_user.email.upper(), password=active_user_data["password"]
        )

        assert isinstance(result, TmsUser)
        assert result.id == active_user.id


@pytest.mark.django_db
class TestMissingAuthenticationValues:
    def test_no_email_returns_none(self, backend, active_user_data):
        result = backend.authenticate(None, password=active_user_data["password"])
        assert result is None

    def test_no_password_returns_none(self, backend, active_user):
        result = backend.authenticate(None, email=active_user.email)
        assert result is None

    def test_empty_email_returns_none(self, backend, active_user_data):
        result = backend.authenticate(None, email="", password=active_user_data["password"])
        assert result is None

    def test_empty_password_returns_none(self, backend, active_user):
        result = backend.authenticate(None, email=active_user.email, password="")
        assert result is None


@pytest.mark.django_db
class TestAuthentication:
    def test_non_existing__user_returns_none(self, backend):
        result = backend.authenticate(None, email="invalid@email.com", password="invalid")
        assert result is None

    def test_wrong_password_returns_none(self, backend, active_user):
        result = backend.authenticate(None, email=active_user.email, password="invalid")
        assert result is None

    def test_inactive_user_returns_none(self, backend, inactive_user, inactive_user_data):
        result = backend.authenticate(
            None, email=inactive_user.email, password=inactive_user_data["password"]
        )
        assert result is None

    def test_user_can_authenticate_returns_false(
        self, backend, active_user, active_user_data, monkeypatch
    ):
        monkeypatch.setattr(backend, "user_can_authenticate", lambda user: False)
        result = backend.authenticate(
            None, email=active_user.email, password=active_user_data["password"]
        )
        assert result is None


@pytest.mark.django_db
class TestTimingAttack:
    @staticmethod
    def calculate_timing_median(backend, iterations, email, password):
        times = []
        for _ in range(iterations):
            cache.clear()
            start = time.perf_counter()
            backend.authenticate(None, email=email, password=password)
            times.append(time.perf_counter() - start)
        return sum(times) / 2

    @pytest.mark.timing
    @pytest.mark.skip
    def test_sca_secure_timing_attack(self, backend, active_user, active_user_data):
        iterations = 10
        threshold_ms = 1000

        avg_existing = self.calculate_timing_median(
            backend, iterations, active_user.email, active_user_data["email"]
        )
        avg_nonexistent = self.calculate_timing_median(
            backend, iterations, email="invalid@email.com", password="invalid"
        )
        delta_ms = abs(avg_existing - avg_nonexistent) * 1000

        assert delta_ms < threshold_ms
