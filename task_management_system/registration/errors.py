from django.utils.translation import gettext_lazy as _

EMAIL_VERIFICATION_TOKEN_DOES_NOT_EXIST = _("Email verification token does not exist.")

PERMISSION_DENIED_TO_CREATE_AN_INACTIVE_USER = _("Not allowed to register a user.")
PERMISSION_DENIED_TO_CREATE_AN_VERIFICATION_TOKEN = _(
    "Not allowed to create a verification token."
)
PERMISSION_DENIED_TO_VERIFY_VERIFICATION_TOKEN = _("Not allowed to verify verification token.")
PERMISSION_DENIED_TO_ACTIVATE_USER = _("Not allowed to verify verification token.")
