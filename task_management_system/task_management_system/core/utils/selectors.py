from django.core.exceptions import MultipleObjectsReturned
from loguru import logger
from rest_framework.exceptions import NotFound
from tms_auth.errors import USER_DOES_NOT_EXIST
from user.models import TmsUser

from task_management_system.core.logging.utils import bind_context_dict


def get_user(user_id: int, update: bool = False) -> TmsUser:
    try:
        bind_context_dict(user=user_id)
        if update:
            logger.debug("Select user for update.")
            user = TmsUser.objects.select_for_update().get(id=user_id)
        else:
            user = TmsUser.objects.get(id=user_id)
        logger.debug("Found: User exists.")
        return user
    except TmsUser.DoesNotExist as exc:
        logger.warning(f"Not found: User not found. Reaseon {exc}.")
        raise NotFound(USER_DOES_NOT_EXIST)
    except MultipleObjectsReturned as exc:
        logger.critical(f"Critical: Multiple Users returned! Reason {exc}.")
        raise
