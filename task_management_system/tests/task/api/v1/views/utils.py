from django.utils.timezone import is_aware
from task.policies import TaskMembershipPolicy, TaskNotePolicy, TaskPolicy
from tests.user.api.v1.utils import parse_user_dict
from user.models import TmsUser


def assert_paginator(data):
    assert set(data.keys()) == {"previous", "next", "results", "count"}


def extract_results(data):
    if isinstance(data, dict) and "results" in data:
        return data["results"]
    return data


def to_iso(dt):
    if is_aware(dt):
        return dt.isoformat().replace("+00:00", "Z")
    return dt.isoformat()


def assert_task_response_body(data, task, actor):
    assert data == {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "created_at": to_iso(task.created_at),
        "can_delete": TaskPolicy.can_delete(actor, task) if isinstance(actor, TmsUser) else False,
        "editable_fields": list(
            TaskPolicy.get_editable_fields(actor, task) if isinstance(actor, TmsUser) else []
        ),
    }


def assert_task_format(data):
    data = extract_results(data)
    assert isinstance(data, list)

    for item in data:
        assert set(item.keys()) == {
            "id",
            "title",
            "description",
            "status",
            "created_at",
            "can_delete",
            "editable_fields",
        }


def assert_task_membership_response_body(data, membership, actor):
    assert data == {
        "id": membership.id,
        "user": parse_user_dict(actor, membership.user),
        "task": membership.task.id,
        "role": membership.role,
        "joined_at": to_iso(membership.joined_at),
        "can_delete": TaskMembershipPolicy.can_delete(actor, membership),
        "editable_fields": list(TaskMembershipPolicy.get_editable_fields(actor, membership)),
    }


def assert_task_membership_format(data):
    data = extract_results(data)
    assert isinstance(data, list)

    for item in data:
        assert set(item.keys()) == {
            "id",
            "user",
            "task",
            "role",
            "joined_at",
            "can_delete",
            "editable_fields",
        }


def assert_task_note_response_body(data, note, actor):
    assert data == {
        "id": note.id,
        "author": parse_user_dict(actor, note.author),
        "task": note.task.id,
        "note": note.note,
        "created_at": to_iso(note.created_at),
        "can_delete": TaskNotePolicy.can_delete(actor, note),
        "editable_fields": list(TaskNotePolicy.get_editable_fields(actor, note)),
    }


def assert_task_note_format(data):
    data = extract_results(data)
    assert isinstance(data, list)

    for item in data:
        assert set(item.keys()) == {
            "id",
            "note",
            "author",
            "task",
            "created_at",
            "can_delete",
            "editable_fields",
        }


def select_data_dict(method, url_name, data_task, data_task_membership, data_task_note):
    match url_name:
        case "list":
            return data_task if method == "post" else {}
        case "detail":
            return {"title": "updated"} if method == "patch" else {}
        case "membership":
            return data_task_membership
        case "note":
            return data_task_note
        case _:
            return {}
