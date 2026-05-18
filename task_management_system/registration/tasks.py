from smtplib import SMTPException

from celery import shared_task
from django.core.mail import send_mail
from django.utils.timezone import now
from loguru import logger
from registration.models import EmailVerificationToken
from user.models import TmsUser

from task_management_system.core.logging.utils import bind_context_dict


@shared_task  # type: ignore[misc]
def cleanup_expired_tokens() -> None:
    cnt, _ = EmailVerificationToken.objects.filter(expires_at__lt=now()).delete()
    logger.trace(f"Deleted {cnt} expired tokens.")


@shared_task(  # type: ignore[misc]
    bind=True,
    autoretry_for=(SMTPException, ConnectionError, TimeoutError),
    retry_backoff=True,
    max_retries=5,
)
def send_verification_email_task(self: object, user_id: int, token_id: int) -> None:
    bind_context_dict(user=user_id, verification_toke=token_id)
    try:
        user = TmsUser.objects.get(pk=user_id)
        token_obj = EmailVerificationToken.objects.get(pk=token_id)

        logger.trace(f"Sending verification mail to {user.email}.")

        send_mail(
            subject="Activate your account",
            message=f"Your code: {token_obj.token}",
            from_email="noreply@tms.org",
            recipient_list=[user.email],
            fail_silently=False,
        )
    except (TmsUser.DoesNotExist, EmailVerificationToken.DoesNotExist):
        logger.trace("Task aborted: User or Token no longer exists.")
