from __future__ import annotations

from typing import Any

from django.core.exceptions import ValidationError
from django.db.models import CASCADE, SET_NULL, DateTimeField, ForeignKey, Model, TextField
from user.models import TmsUser

from .task import Task


class TaskNote(Model):  # type: ignore[misc]
    note = TextField(blank=False, null=False)
    author = ForeignKey(TmsUser, on_delete=SET_NULL, null=True, blank=True)
    task = ForeignKey(Task, on_delete=CASCADE, related_name="notes")
    created_at = DateTimeField(auto_now_add=True)

    def clean(self) -> None:
        super().clean()

        if self.author and not self.task.members.filter(pk=self.author.pk).exists():
            raise ValidationError("Author must be a member of the task.")

    def save(self, *args: Any, **kwargs: Any) -> None:
        if not kwargs.pop("skip_validation", False):
            self.full_clean()
        super().save(*args, **kwargs)
