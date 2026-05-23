import pytest
from factory import SubFactory, django, fuzzy
from fixtures.task import TaskFactory
from fixtures.user import SuperuserFactory, UserFactory
from task.models import Role, TaskMembership

POSSIBLE_ROLES = [Role.ADMIN, Role.MEMBER, Role.VIEWER]


class TaskMembershipFactory(django.DjangoModelFactory):
    class Meta:
        model = TaskMembership

    user = SubFactory(UserFactory)
    task = SubFactory(TaskFactory)
    role = fuzzy.FuzzyChoice(POSSIBLE_ROLES)


@pytest.fixture
def task_memberships(db, task, users):
    TaskMembershipFactory.create_batch(5, task=task)


@pytest.fixture
def task_membership(db, task, users):
    return TaskMembershipFactory(task=task)


@pytest.fixture
def five_users(db):
    return UserFactory.create_batch(5)


@pytest.fixture
def member_is_owner(db, task, five_users):
    return five_users[0], TaskMembershipFactory(user=five_users[0], task=task, role=Role.OWNER)


@pytest.fixture
def member_is_admin(db, task, five_users):
    return five_users[1], TaskMembershipFactory(user=five_users[1], task=task, role=Role.ADMIN)


@pytest.fixture
def member_is_member(db, task, five_users):
    return five_users[2], TaskMembershipFactory(user=five_users[2], task=task, role=Role.MEMBER)


@pytest.fixture
def member_is_viewer(db, task, five_users):
    return five_users[3], TaskMembershipFactory(user=five_users[3], task=task, role=Role.VIEWER)


@pytest.fixture
def superuser_is_not_member(db, task, five_users):
    return SuperuserFactory(), None


@pytest.fixture
def user_is_not_member(db, five_users):
    return five_users[4], None
