import pytest
from tms_auth.backends import TmsEmailBackend


@pytest.fixture
def backend():
    return TmsEmailBackend()
