from rest_framework.throttling import AnonRateThrottle


class ActivateUserThrottle(AnonRateThrottle):  # type: ignore[misc]
    scope = "activate_user"
