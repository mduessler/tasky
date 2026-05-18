from rest_framework.throttling import UserRateThrottle


class TaskMembershipReadBurst(UserRateThrottle):  # type: ignore[misc]
    scope = "task_membership_read_burst"


class TaskMembershipReadSustained(UserRateThrottle):  # type: ignore[misc]
    scope = "task_membership_read_sustained"


class TaskMembershipCreateBurst(UserRateThrottle):  # type: ignore[misc]
    scope = "task_membership_create_burst"


class TaskMembershipCreateSustained(UserRateThrottle):  # type: ignore[misc]
    scope = "task_membership_create_sustained"


class TaskMembershipUpdateBurst(UserRateThrottle):  # type: ignore[misc]
    scope = "task_membership_update_burst"


class TaskMembershipUpdateSustained(UserRateThrottle):  # type: ignore[misc]
    scope = "task_membership_update_sustained"


class TaskMembershipDeleteBurst(UserRateThrottle):  # type: ignore[misc]
    scope = "task_membership_delete_burst"


class TaskMembershipDeleteSustained(UserRateThrottle):  # type: ignore[misc]
    scope = "task_membership_delete_sustained"
