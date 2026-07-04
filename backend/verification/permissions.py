from rest_framework.permissions import BasePermission, SAFE_METHODS

from users.models import KYCStatus


class IsVerifiedUser(BasePermission):
    """
    Trust-first gate: deny POST, PUT, PATCH, and DELETE on protected views
    unless the authenticated user has kyc_status == APPROVED.

    Safe methods (GET, HEAD, OPTIONS) are always permitted for authenticated
    users when combined with IsAuthenticated.
    """

    message = "Identity verification required. Complete KYC before interacting with listings."

    def has_permission(self, request, view) -> bool:
        if request.method in SAFE_METHODS:
            return True

        user = request.user
        if not user or not user.is_authenticated:
            return False

        return user.kyc_status == KYCStatus.APPROVED
