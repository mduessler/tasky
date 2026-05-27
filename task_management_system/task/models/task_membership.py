from __future__ import annotations

from typing import Any

from django.core.exceptions import ValidationError
from django.db.models import (
    CASCADE,
    CharField,
    DateTimeField,
    ForeignKey,
    Model,
    Q,
    TextChoices,
    UniqueConstraint,
)
from user.models import TmsUser

from .task import Task


class Role(TextChoices):  # type: ignore[misc]
    OWNER = "owner", "Owner"
    ADMIN = "admin", "Admin"
    MEMBER = "member", "Member"
    VIEWER = "viewer", "Viewer"


class TaskMembership(Model):  # type: ignore[misc]
    user = ForeignKey(TmsUser, on_delete=CASCADE)
    task = ForeignKey(Task, on_delete=CASCADE, related_name="memberships")
    role = CharField(max_length=10, choices=Role.choices)
    joined_at = DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            UniqueConstraint(fields=["user", "task"], name="unique_user_task"),
            UniqueConstraint(
                fields=["task"],
                condition=Q(role=Role.OWNER),
                name="unique_task_owner",
            ),
        ]

    def clean(self) -> None:
        super().clean()
        if self.role not in Role.values:
            raise ValidationError({"role": "Invalid role."})

    def save(self, *args: Any, **kwargs: Any) -> None:
        if not kwargs.pop("skip_validation", False):
            self.full_clean()
        super().save(*args, **kwargs)

    @staticmethod
    def get_user_role(user: TmsUser | None, task: Task | None) -> Role | None:
        if not user or not task:
            return None

        membership = TaskMembership.objects.filter(user=user, task=task).only("role").first()

        return Role(membership.role) if membership else None

    def __str__(self) -> str:
        return f"{self.user.pk} - {self.task.pk} ({self.role})"
