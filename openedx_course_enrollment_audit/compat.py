"""
Proxies and compatibility code for edx-platform features.

This module moderates access to all edx-platform features allowing for cross-version compatibility code.
It also simplifies running tests outside edx-platform's environment by stubbing these functions in unit tests.
"""
from __future__ import annotations

from django.conf import settings


def get_manual_enrollment_audit_model():
    """Get the manual enrollment audit model from Open edX."""
    if getattr(settings, 'TESTING', False):
        # Use the basic object for testing
        return object

    # noinspection PyUnresolvedReferences,PyPackageRequirements
    from common.djangoapps.student.models import ManualEnrollmentAudit

    return ManualEnrollmentAudit
