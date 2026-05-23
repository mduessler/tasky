import pytest
from django.contrib.auth.models import AnonymousUser
from factory import LazyAttribute, PostGenerationMethodCall, Sequence, django
from user.models import TmsUser

from task_management_system.utils import TEST_DATA

USERS = TEST_DATA / "auth" / "user.json"


class UserFactory(django.DjangoModelFactory):
    class Meta:
        model = TmsUser

    username = Sequence(lambda n: f"user_{n}")
    email = LazyAttribute(lambda o: f"{o.username}@example.com")
    password = PostGenerationMethodCall("set_password", "ThisIsATestingPassword")
    is_staff = False
    is_superuser = False


class SuperuserFactory(UserFactory):
    is_superuser = True
    is_staff = True


@pytest.fixture
def users(db):
    UserFactory.create_batch(20)


@pytest.fixture
def active_user_data():
    return {
        "password": "ThisIsATestingPassword",
        "username": "ZockerHeld99",
        "first_name": "Max",
        "last_name": "Mustermann",
        "email": "max@example.com",
        "is_active": True,
    }


@pytest.fixture
def inactive_user_data():
    return {
        "password": "ThisIsATestingPassword",
        "username": "NoobMaster",
        "first_name": "Kevin",
        "last_name": "Müller",
        "email": "kevin@example.com",
        "is_active": False,
    }


@pytest.fixture
def superuser_data():
    return {
        "password": "ThisIsATestingPassword",
        "username": "PixelQueen",
        "first_name": "Sarah",
        "last_name": "Schmidt",
        "email": "sara@example.com",
        "is_active": True,
    }


@pytest.fixture
def active_user(db, active_user_data):
    return UserFactory(**active_user_data)


@pytest.fixture
def inactive_user(db, inactive_user_data):
    return UserFactory(**inactive_user_data)


@pytest.fixture
def superuser(db, superuser_data):
    return SuperuserFactory(**superuser_data)


@pytest.fixture
def anonymous_user():
    return AnonymousUser()


@pytest.fixture(scope="class")
def users_read_only(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        UserFactory.create_batch(20)


@pytest.fixture(scope="class")
def active_user_data_read_only():
    return {
        "password": "ThisIsATestingPassword",
        "username": "ZockerHeld99",
        "first_name": "Max",
        "last_name": "Mustermann",
        "email": "max@example.com",
        "is_active": True,
    }


@pytest.fixture(scope="class")
def inactive_user_data_read_only():
    return {
        "password": "ThisIsATestingPassword",
        "username": "NoobMaster",
        "first_name": "Kevin",
        "last_name": "Müller",
        "email": "kevin@example.com",
        "is_active": False,
    }


@pytest.fixture(scope="class")
def superuser_data_read_only():
    return {
        "password": "ThisIsATestingPassword",
        "username": "PixelQueen",
        "first_name": "Sarah",
        "last_name": "Schmidt",
        "email": "sara@example.com",
        "is_active": True,
    }


@pytest.fixture(scope="class")
def active_user_read_only(django_db_setup, django_db_blocker, active_user_data_read_only):
    with django_db_blocker.unblock():
        return UserFactory(**active_user_data_read_only)


@pytest.fixture(scope="class")
def inactive_user_read_only(django_db_setup, django_db_blocker, inactive_user_data_read_only):
    with django_db_blocker.unblock():
        return UserFactory(**inactive_user_data_read_only)


@pytest.fixture(scope="class")
def superuser_read_only(django_db_setup, django_db_blocker, superuser_data_read_only):
    with django_db_blocker.unblock():
        return SuperuserFactory(**superuser_data_read_only)


@pytest.fixture(scope="class")
def anonymous_user_read_only():
    return AnonymousUser()
