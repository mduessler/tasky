import pytest
from factory import Sequence, django, fuzzy
from task.models import Task, TaskStatus

from task_management_system.utils import TEST_DATA

TASKS_FILE = TEST_DATA / "task" / "tasks.json"
TASKS_MEMBERSHIP_FILE = TEST_DATA / "task" / "task_memberships.json"
TASK_NOTES_FILE = TEST_DATA / "task" / "task_notes.json"


class TaskFactory(django.DjangoModelFactory):
    class Meta:
        model = Task

    title = Sequence(lambda n: f"Task {n}")
    description = fuzzy.FuzzyText(length=100)
    status = fuzzy.FuzzyChoice(TaskStatus.values)


@pytest.fixture
def tasks(db):
    TaskFactory.create_batch(10)


@pytest.fixture
def task_data():
    return {
        "title": "This is just a test task",
        "description": "This task is just for testing purposes. Please keep that in mind.",
        "status": "todo",
    }


@pytest.fixture
def task(db, task_data):
    return TaskFactory(**task_data)
