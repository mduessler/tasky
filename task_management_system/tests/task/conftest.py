from datetime import timedelta

import pytest
from django.utils import timezone
from fixtures.task_note import TaskNoteFactory
from task.models import TaskNote


@pytest.fixture(autouse=True)
def memberships_of_task(member_is_owner, member_is_admin, member_is_member, member_is_viewer):
    pass


@pytest.fixture
def expired_task_note(db, task, member_is_owner):
    note = TaskNoteFactory(
        note="This is just a test note.",
        author=member_is_owner[0],
        task=task,
    )
    TaskNote.objects.filter(pk=note.pk).update(created_at=timezone.now() - timedelta(hours=3))
    note.refresh_from_db()
    return note


@pytest.fixture
@pytest.mark.django_db
def user_is_none():
    return None, None


@pytest.fixture
def data_task():
    return {
        "title": "A new title.",
        "description": "This project is very important.",
        "status": "done",
    }


@pytest.fixture
def data_task_membership(task, user_is_not_member):
    user, _ = user_is_not_member
    return {"role": "member", "task": task.id, "user_id": user.id}


@pytest.fixture
def data_task_note_author_is_member(task, member_is_member):
    user, _ = member_is_member
    return {"note": "A very important Note", "task": task.id, "author_id": user.id}


@pytest.fixture
def data_task_note(task, user_is_not_member):
    user, _ = user_is_not_member
    return {"note": "A very important Note", "task": task.id, "author_id": user.id}
