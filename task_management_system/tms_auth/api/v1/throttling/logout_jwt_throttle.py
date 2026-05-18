from rest_framework.throttling import UserRateThrottle


class LogoutJwtThrottleBurst(UserRateThrottle):  # type: ignore[misc]
    scope = "logout_jwt_burst"


class LogoutJwtThrottleSustained(UserRateThrottle):  # type: ignore[misc]
    scope = "logout_jwt_sustained"
