from tests.utils import extract_results
from user.policies import TmsUserPolicy


def parse_user_dict(actor, user):
    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "can_delete": TmsUserPolicy.can_delete(actor, user),
        "editable_fields": list(TmsUserPolicy.get_editable_fields(actor, user)),
    }


def assert_user_response_body(data, user, actor):
    user_dict = parse_user_dict(actor, user)
    assert data == user_dict


def assert_user_format(data):
    data = extract_results(data)
    assert isinstance(data, list)

    for item in data:
        assert set(item.keys()) == {"id", "email", "username", "first_name", "last_name"}
