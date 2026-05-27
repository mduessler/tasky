from __future__ import annotations

from typing import Any

from django.core.exceptions import ValidationError
from django.db.models import CharField, DateTimeField, ManyToManyField, Model, TextField
from user.models import TmsUser

from .task_status import TaskStatus


class Task(Model):  # type: ignore[misc]
    title = CharField(max_length=255)
    description = TextField()
    status = CharField(
        max_length=10,
        choices=TaskStatus.choices,
        default=TaskStatus.TODO,
    )
    members: ManyToManyField[TmsUser, Task] = ManyToManyField(
        TmsUser,
        through="TaskMembership",
        related_name="tasks",
    )
    created_at = DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.title  # type: ignore[no-any-return]

    def clean(self) -> None:
        super().clean()
        if not self.title.strip():
            raise ValidationError({"title": "Title cannot be empty or whitespace."})

    def save(self, *args: Any, **kwargs: Any) -> None:
        if not kwargs.pop("skip_validation", False):
            self.full_clean()
        super().save(*args, **kwargs)
