from rest_framework.parsers import JSONParser
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory, force_authenticate, urlencode


class FakeView:
    def __init__(self, action):
        self.action = action


def get_fake_view(action):
    return FakeView(action)


def build_request(method, user, data=None, query_params=None):
    factory = APIRequestFactory()

    url = "/"
    if query_params:
        url = f"/?{urlencode(query_params, doseq=True)}"
    django_request = getattr(factory, method)(url, data=data or {}, format="json")
    force_authenticate(django_request, user=user)

    return Request(django_request, parsers=[JSONParser()])
