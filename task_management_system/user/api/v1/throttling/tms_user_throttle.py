from rest_framework.throttling import UserRateThrottle


class TmsUserReadBurst(UserRateThrottle):  # type: ignore[misc]
    scope = "tms_user_read_burst"


class TmsUserReadSustained(UserRateThrottle):  # type: ignore[misc]
    scope = "tms_user_read_sustained"


class TmsUserCreateBurst(UserRateThrottle):  # type: ignore[misc]
    scope = "tms_user_create_burst"


class TmsUserCreateSustained(UserRateThrottle):  # type: ignore[misc]
    scope = "tms_user_create_sustained"


class TmsUserUpdateBurst(UserRateThrottle):  # type: ignore[misc]
    scope = "tms_user_update_burst"


class TmsUserUpdateSustained(UserRateThrottle):  # type: ignore[misc]
    scope = "tms_user_update_sustained"


class TmsUserDeleteBurst(UserRateThrottle):  # type: ignore[misc]
    scope = "tms_user_delete_burst"


class TmsUserDeleteSustained(UserRateThrottle):  # type: ignore[misc]
    scope = "tms_user_delete_sustained"
