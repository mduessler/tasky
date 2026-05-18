from django.db.models.enums import TextChoices


class TaskStatus(TextChoices):  # type: ignore[misc]
    TODO = "todo", "To Do"
    DOING = "doing", "Doing"
    DONE = "done", "Done"
