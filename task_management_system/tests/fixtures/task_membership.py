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


@pytest.fixture(scope="class")
def task_memberships_read_only(
    django_db_setup, django_db_blocker, task_read_only, users_read_only
):
    with django_db_blocker.unblock():
        TaskMembershipFactory.create_batch(5, task=task_read_only)


@pytest.fixture(scope="class")
def task_membership_read_only(django_db_setup, django_db_blocker, task_read_only, users_read_only):
    with django_db_blocker.unblock():
        return TaskMembershipFactory(task=task_read_only)


@pytest.fixture(scope="class")
def five_users_read_only(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        return UserFactory.create_batch(5)


@pytest.fixture(scope="class")
def member_is_owner_read_only(
    django_db_setup, django_db_blocker, task_read_only, five_users_read_only
):
    with django_db_blocker.unblock():
        return five_users_read_only[0], TaskMembershipFactory(
            user=five_users_read_only[0], task=task_read_only, role=Role.OWNER
        )


@pytest.fixture(scope="class")
def member_is_admin_read_only(
    django_db_setup, django_db_blocker, task_read_only, five_users_read_only
):
    with django_db_blocker.unblock():
        return five_users_read_only[1], TaskMembershipFactory(
            user=five_users_read_only[1], task=task_read_only, role=Role.ADMIN
        )


@pytest.fixture(scope="class")
def member_is_member_read_only(
    django_db_setup, django_db_blocker, task_read_only, five_users_read_only
):
    with django_db_blocker.unblock():
        return five_users_read_only[2], TaskMembershipFactory(
            user=five_users_read_only[2], task=task_read_only, role=Role.MEMBER
        )


@pytest.fixture(scope="class")
def member_is_viewer_read_only(
    django_db_setup, django_db_blocker, task_read_only, five_users_read_only
):
    with django_db_blocker.unblock():
        return five_users_read_only[3], TaskMembershipFactory(
            user=five_users_read_only[3], task=task_read_only, role=Role.VIEWER
        )


@pytest.fixture(scope="class")
def superuser_is_not_member_read_only(
    django_db_setup, django_db_blocker, task_read_only, five_users_read_only
):
    with django_db_blocker.unblock():
        return SuperuserFactory(), None


@pytest.fixture(scope="class")
def user_is_not_member_read_only(five_users_read_only):
    return five_users_read_only[4], None
