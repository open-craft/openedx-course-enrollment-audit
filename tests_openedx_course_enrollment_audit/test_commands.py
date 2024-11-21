import pytest
from common.djangoapps.student.models import CourseEnrollment, ManualEnrollmentAudit, UNENROLLED_TO_ENROLLED
from common.djangoapps.student.tests.factories import UserFactory
from django.core.management import call_command
from django.db.models.signals import post_save
from opaque_keys.edx.keys import CourseKey

from openedx_course_enrollment_audit.models import CourseEnrollmentAudit
from .test_models import disconnect_all_signals


@pytest.fixture
def create_enrollment():
    """Create a course enrollment for specified user and course."""

    def _create_enrollment(user, course_id):
        with disconnect_all_signals(post_save):
            enrollment = CourseEnrollment.objects.create(user=user, course_id=course_id)
        return enrollment

    return _create_enrollment


@pytest.fixture
def create_manual_enrollment_audit():
    """Create a manual enrollment audit for specified enrollment."""

    def _create_manual_enrollment_audit(enrollment):
        with disconnect_all_signals(post_save):
            audit = ManualEnrollmentAudit.objects.create(
                enrollment=enrollment,
                enrolled_email=enrollment.user.email,
                state_transition=UNENROLLED_TO_ENROLLED,
            )
        return audit

    return _create_manual_enrollment_audit


@pytest.mark.django_db
def test_backfill_course_enrollment_audit_command(create_enrollment, create_manual_enrollment_audit):
    """Test that the management command correctly backfills CourseEnrollmentAudit records."""

    user = UserFactory.create()
    user2 = UserFactory.create()

    course_id = CourseKey.from_string("course-v1:edX+DemoX+Demo_Course")
    course_id2 = CourseKey.from_string("course-v1:edX+DemoX+Demo_Course2")

    enrollment = create_enrollment(user, course_id)
    enrollment2 = create_enrollment(user2, course_id2)
    enrollment3 = create_enrollment(user, course_id2)
    enrollment4 = create_enrollment(user2, course_id)

    create_manual_enrollment_audit(enrollment)
    create_manual_enrollment_audit(enrollment2)
    create_manual_enrollment_audit(enrollment3)
    create_manual_enrollment_audit(enrollment4)
    create_manual_enrollment_audit(enrollment3)

    assert CourseEnrollmentAudit.objects.count() == 0

    call_command("backfill_course_enrollment_audit")

    assert CourseEnrollmentAudit.objects.count() == 4


@pytest.mark.django_db
def test_backfill_course_enrollment_audit_no_records():
    """Test that the management command handles the case where there are no ManualEnrollmentAudit records."""
    assert ManualEnrollmentAudit.objects.count() == 0
    call_command("backfill_course_enrollment_audit")
    assert CourseEnrollmentAudit.objects.count() == 0
