import pytest
from factory import SubFactory, django, fuzzy
from fixtures.task import TaskFactory
from fixtures.user import UserFactory
from task.models import TaskMembership, TaskNote


class TaskNoteFactory(django.DjangoModelFactory):
    class Meta:
        model = TaskNote

    note = fuzzy.FuzzyText(length=200)
    author = SubFactory(UserFactory)
    task = SubFactory(TaskFactory)


@pytest.fixture
def task_note(db, task, member_is_owner):
    return TaskNoteFactory(note="This is just a test note.", author=member_is_owner[0], task=task)


@pytest.fixture
def task_notes(db, task, task_memberships):
    for membership in TaskMembership.objects.filter(task=task):
        TaskNoteFactory.create_batch(4, task=task, author=membership.user)


@pytest.fixture(scope="class")
def task_note_read_only(
    django_db_setup, django_db_blocker, task_read_only, member_is_owner_read_only
):
    with django_db_blocker.unblock():
        return TaskNoteFactory(
            note="This is just a test note.",
            author=member_is_owner_read_only[0],
            task=task_read_only,
        )


@pytest.fixture(scope="class")
def task_notes_read_only(
    django_db_setup, django_db_blocker, task_read_only, task_memberships_read_only
):
    with django_db_blocker.unblock():
        for membership in TaskMembership.objects.filter(task=task_read_only):
            TaskNoteFactory.create_batch(4, task=task_read_only, author=membership.user)
