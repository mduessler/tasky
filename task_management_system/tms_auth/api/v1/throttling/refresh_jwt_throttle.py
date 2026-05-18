from rest_framework.throttling import UserRateThrottle


class RefreshJwtThrottleBurst(UserRateThrottle):  # type: ignore[misc]
    scope = "refresh_jwt_burst"


class RefreshJwtThrottleSustained(UserRateThrottle):  # type: ignore[misc]
    scope = "refresh_jwt_sustained"
