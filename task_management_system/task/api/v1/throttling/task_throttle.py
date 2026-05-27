from rest_framework.throttling import UserRateThrottle


class TaskReadBurst(UserRateThrottle):  # type: ignore[misc]
    scope = "task_read_burst"


class TaskReadSustained(UserRateThrottle):  # type: ignore[misc]
    scope = "task_read_sustained"


class TaskCreateBurst(UserRateThrottle):  # type: ignore[misc]
    scope = "task_create_burst"


class TaskCreateSustained(UserRateThrottle):  # type: ignore[misc]
    scope = "task_create_sustained"


class TaskUpdateBurst(UserRateThrottle):  # type: ignore[misc]
    scope = "task_update_burst"


class TaskUpdateSustained(UserRateThrottle):  # type: ignore[misc]
    scope = "task_update_sustained"


class TaskDeleteBurst(UserRateThrottle):  # type: ignore[misc]
    scope = "task_delete_burst"


class TaskDeleteSustained(UserRateThrottle):  # type: ignore[misc]
    scope = "task_delete_sustained"
