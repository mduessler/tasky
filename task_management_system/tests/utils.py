from django.conf import settings
from django.test import override_settings
from django.urls import reverse
from django.utils.timezone import is_aware
from rest_framework.parsers import JSONParser
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory, force_authenticate, urlencode
from rest_framework.views import APIView


class DummyView(APIView):
    def __init__(self, action=None):
        if action is not None:
            self.action = action


def build_django_request(method, user, path="/", data=None, query_params=None):
    method = method.lower()
    factory = APIRequestFactory()

    if query_params:
        path = f"{path}?{urlencode(query_params, doseq=True)}"

    request = getattr(factory, method)(path, data=data or {}, format="json")
    request.user = user

    return request


def build_request(method, user, path="/", data=None, query_params=None):
    method = method.lower()
    factory = APIRequestFactory()

    if query_params:
        path = f"{path}?{urlencode(query_params, doseq=True)}"
    django_request = getattr(factory, method)(path, data=data or {}, format="json")
    if user:
        force_authenticate(django_request, user=user)

    return Request(django_request, parsers=[JSONParser()])


def assert_log(record, msg, level, **kwargs):
    assert msg in record["message"]
    assert record["level"].name == level

    for key, value in kwargs.items():
        assert record["extra"][key] == value


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


def parse_url(basename, url_name, obj_pk=None):
    if url_name == "list":
        return reverse(f"{basename}-{url_name}")
    else:
        return reverse(f"{basename}-{url_name}", kwargs={"pk": obj_pk})


def assert_burst_throttle(
    actor,
    url,
    method,
    api_client,
    key,
    burst_rate,
    sustained_rate,
    burst_class,
    sustained_class,
    data={},
):
    with override_settings(
        REST_FRAMEWORK={
            **settings.REST_FRAMEWORK,
            "DEFAULT_THROTTLE_RATES": {
                f"{key}_burst": f"{burst_rate}/min",
                f"{key}_sustained": f"{sustained_rate}/min",
            },
        }
    ):
        setattr(burst_class, "rate", f"{burst_rate}/min")
        setattr(sustained_class, "rate", f"{sustained_rate}/min")

        if actor:
            api_client.force_authenticate(user=actor)

        method_func = getattr(api_client, method)

        for _ in range(burst_rate):
            response = method_func(url, data=data)
            assert response.status_code in {200, 201, 202, 204}

        response = method_func(url, data=data)
    assert response.status_code == 429


def assert_sustained_throttle(
    actor,
    url,
    method,
    api_client,
    key,
    burst_rate,
    sustained_rate,
    burst_class,
    sustained_class,
    data={},
):
    with override_settings(
        REST_FRAMEWORK={
            **settings.REST_FRAMEWORK,
            "DEFAULT_THROTTLE_RATES": {
                f"{key}_burst": f"{burst_rate}/min",
                f"{key}_sustained": f"{sustained_rate}/min",
            },
        }
    ):
        setattr(burst_class, "rate", f"{burst_rate}/min")
        setattr(sustained_class, "rate", f"{sustained_rate}/min")

        if actor:
            api_client.force_authenticate(user=actor)
        method_func = getattr(api_client, method)

        for _ in range(sustained_rate):
            response = method_func(url, data=data)
            assert response.status_code in {200, 201, 204}

        response = method_func(url, data=data)
    assert response.status_code == 429
