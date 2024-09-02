from unittest.mock import patch, MagicMock
from django.db.models.signals import post_save

from openedx_course_enrollment_audit.compat import get_manual_enrollment_audit_model


@patch('openedx_course_enrollment_audit.models.CourseEnrollmentAudit.create_from_manual_enrollment')
def test_sync_course_enrollment_audit_signal(mock_create_from_manual_enrollment):
    mock_manual_enrollment_audit_instance = MagicMock(
        enrolled_email='test@example.com',
        course_id='course-v1:edX+DemoX+Demo_Course',
        enrollment=MagicMock(),
        state_transition='enrolled',
        reason='{"org": "edX", "course_id": "course-v1:edX+DemoX+Demo_Course", "role": "student", "reason": "manual"}'
    )
    post_save.send(sender=get_manual_enrollment_audit_model(), instance=mock_manual_enrollment_audit_instance,
                   created=True)
    mock_create_from_manual_enrollment.assert_called_once_with(mock_manual_enrollment_audit_instance)
