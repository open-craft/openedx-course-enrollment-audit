"""
openedx_course_enrollment_audit Django application initialization.
"""

from django.apps import AppConfig


class OpenedxCourseEnrollmentAuditConfig(AppConfig):
    """
    Configuration for the openedx_course_enrollment_audit Django application.
    """

    name = "openedx_course_enrollment_audit"

    plugin_app = {
        "signals_config": {
            "lms.djangoapp": {
                "relative_path": "signals",
            }
        },
    }

    def ready(self):
        """
        Import signals so they are registered.
        """
        from openedx_course_enrollment_audit import signals  # pylint: disable=unused-import
