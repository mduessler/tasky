import pytest


@pytest.fixture(autouse=True)
def clear_cache_auto(clear_cache):
    pass
