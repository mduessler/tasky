from rest_framework.throttling import AnonRateThrottle


class RegisterUserThrottle(AnonRateThrottle):  # type: ignore[misc]
    scope = "register_user"
