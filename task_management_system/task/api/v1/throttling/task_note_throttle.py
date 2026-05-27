from rest_framework.throttling import UserRateThrottle


class TaskNoteReadBurst(UserRateThrottle):  # type: ignore[misc]
    scope = "task_note_read_burst"


class TaskNoteReadSustained(UserRateThrottle):  # type: ignore[misc]
    scope = "task_note_read_sustained"


class TaskNoteCreateBurst(UserRateThrottle):  # type: ignore[misc]
    scope = "task_note_create_burst"


class TaskNoteCreateSustained(UserRateThrottle):  # type: ignore[misc]
    scope = "task_note_create_sustained"


class TaskNoteUpdateBurst(UserRateThrottle):  # type: ignore[misc]
    scope = "task_note_update_burst"


class TaskNoteUpdateSustained(UserRateThrottle):  # type: ignore[misc]
    scope = "task_note_update_sustained"


class TaskNoteDeleteBurst(UserRateThrottle):  # type: ignore[misc]
    scope = "task_note_delete_burst"


class TaskNoteDeleteSustained(UserRateThrottle):  # type: ignore[misc]
    scope = "task_note_delete_sustained"
