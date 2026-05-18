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
