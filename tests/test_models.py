from unittest.mock import MagicMock, patch
import pytest

from openedx_course_enrollment_audit.models import CourseEnrollmentAudit


@pytest.fixture
def mock_manual_enrollment_audit():
    mock_audit = MagicMock()
    mock_audit.enrolled_email = 'test@example.com'
    mock_audit.enrollment = MagicMock(user_id=42)
    mock_audit.state_transition = 'enrolled'
    mock_audit.reason = '{"org": "edX", "course_id": "course-v1:edX+DemoX+Demo_Course", "role": "student", "reason": "manual"}'
    return mock_audit


@patch('openedx_course_enrollment_audit.models.CourseEnrollmentAudit.objects')
def test_create_from_manual_enrollment(mock_objects, mock_manual_enrollment_audit):
    """Simulate the creation of a new CourseEnrollmentAudit instance."""
    mock_course_enrollment_audit = MagicMock(
        enrolled_email='test@example.com',
        course_id='course-v1:edX+DemoX+Demo_Course',
        role='student'
    )
    mock_objects.update_or_create.return_value = (mock_course_enrollment_audit, True)

    course_enrollment_audit, created = CourseEnrollmentAudit.create_from_manual_enrollment(mock_manual_enrollment_audit)

    assert created is True
    assert course_enrollment_audit.enrolled_email == 'test@example.com'
    assert course_enrollment_audit.course_id == 'course-v1:edX+DemoX+Demo_Course'
    assert course_enrollment_audit.role == 'student'


@patch('openedx_course_enrollment_audit.models.CourseEnrollmentAudit.objects')
def test_update_existing_course_enrollment_audit(mock_objects, mock_manual_enrollment_audit):
    """Simulate the update of an existing CourseEnrollmentAudit instance."""
    mock_course_enrollment_audit = MagicMock(
        enrolled_email='test@example.com',
        course_id='course-v1:edX+DemoX+Demo_Course',
        role='admin'
    )
    mock_objects.update_or_create.return_value = (mock_course_enrollment_audit, False)

    # First creation
    CourseEnrollmentAudit.create_from_manual_enrollment(mock_manual_enrollment_audit)

    # Update reason
    mock_manual_enrollment_audit.reason = '{"org": "edX", "course_id": "course-v1:edX+DemoX+Demo_Course", "role": "admin", "reason": "updated"}'

    course_enrollment_audit, created = CourseEnrollmentAudit.create_from_manual_enrollment(mock_manual_enrollment_audit)

    assert created is False
    assert course_enrollment_audit.role == 'admin'
