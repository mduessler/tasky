from rest_framework.throttling import AnonRateThrottle


class LoginJwtThrottleBurst(AnonRateThrottle):  # type: ignore[misc]
    scope = "login_jwt_burst"


class LoginJwtThrottleSustained(AnonRateThrottle):  # type: ignore[misc]
    scope = "login_jwt_sustained"
