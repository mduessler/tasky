from unittest.mock import patch

import pytest
from tests.utils import build_request
from user.api.v1.serializers import TmsUserWriteSerializer


@pytest.mark.django_db
class TestServiceHandoff:

    @patch("user.services.TmsUserService.update")
    def test_update_handoff_to_service(
        self, mock_update, active_user, inactive_user, inactive_user_data
    ):
        mock_update.return_value = True

        serializer = TmsUserWriteSerializer(
            instance=inactive_user,
            data=inactive_user_data,
            partial=True,
            context={"request": build_request("post", active_user)},
        )

        assert serializer.is_valid() is True

        serializer.save()

        mock_update.assert_called_once_with(
            active_user, inactive_user.id, serializer.validated_data
        )
