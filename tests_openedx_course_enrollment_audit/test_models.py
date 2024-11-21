"""Tests for the CourseEnrollmentAudit model."""

from typing import Callable

import factory
import pytest
from common.djangoapps.student.models import (
    ENROLLED_TO_UNENROLLED,
    UNENROLLED_TO_ENROLLED,
    CourseEnrollment,
    ManualEnrollmentAudit,
)
from common.djangoapps.student.tests.factories import UserFactory
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from opaque_keys.edx.keys import CourseKey

from openedx_course_enrollment_audit.models import CourseEnrollmentAudit


@pytest.fixture
def user() -> User:
    """Create a user for testing."""
    return UserFactory.create()


@pytest.fixture
@factory.django.mute_signals(post_save)
def enrollment(user: User) -> CourseEnrollment:
    """Create a course enrollment for testing."""
    return CourseEnrollment.objects.create(
        user=user,
        course_id=CourseKey.from_string("course-v1:edX+DemoX+Demo_Course"),
    )


@pytest.fixture
def create_manual_enrollment_audit(enrollment) -> Callable[..., ManualEnrollmentAudit]:
    """Create a manual enrollment audit for the specified enrollment."""

    def _create_manual_enrollment_audit(
        enrolled_email=None,
        state_transition=UNENROLLED_TO_ENROLLED,
        role=None,
        reason=None,
        enrolled_by=None,
    ) -> ManualEnrollmentAudit:
        return ManualEnrollmentAudit.objects.create(
            enrollment=enrollment,
            enrolled_email=enrolled_email or enrollment.user.email,
            enrolled_by=enrolled_by,
            state_transition=state_transition,
            role=role,
            reason=reason,
        )

    return _create_manual_enrollment_audit


@pytest.mark.django_db
def test_create_from_manual_enrollment(user, enrollment, create_manual_enrollment_audit):
    """Test the creation of a new CourseEnrollmentAudit instance."""
    staff_user = UserFactory.create()

    assert CourseEnrollmentAudit.objects.count() == 0

    audit = create_manual_enrollment_audit(enrolled_email="test@example.com", enrolled_by=staff_user, role="student")

    assert CourseEnrollmentAudit.objects.count() == 1
    course_enrollment_audit = CourseEnrollmentAudit.objects.first()

    assert course_enrollment_audit.manual_enrollment_audit == audit
    assert course_enrollment_audit.enrollment == enrollment
    assert course_enrollment_audit.time_stamp == audit.time_stamp
    assert course_enrollment_audit.enrolled_email == audit.enrolled_email
    assert course_enrollment_audit.course_id == str(audit.enrollment.course_id)
    assert course_enrollment_audit.role == audit.role
    assert course_enrollment_audit.user_id == audit.enrollment.user_id
    assert course_enrollment_audit.enrolled_by == audit.enrolled_by
    assert course_enrollment_audit.state_transition == audit.state_transition
    assert course_enrollment_audit.reason is None
    assert course_enrollment_audit.org is None


@pytest.mark.django_db
def test_parse_reason(user, enrollment, create_manual_enrollment_audit):
    """Test parsing of the reason field with valid JSON."""
    reason = '{"org": "edX", "course_id": "test_course", "role": "learner", "reason": "manual"}'
    create_manual_enrollment_audit(role="student", reason=reason)

    course_enrollment_audit = CourseEnrollmentAudit.objects.first()
    assert course_enrollment_audit.course_id == "test_course"
    assert course_enrollment_audit.role == "learner"
    assert course_enrollment_audit.enrolled_by is None
    assert course_enrollment_audit.org == "edX"
    assert course_enrollment_audit.reason == "manual"


@pytest.mark.django_db
def test_parse_reason_invalid_json(user, enrollment, create_manual_enrollment_audit):
    """Test parsing of the reason field with invalid JSON."""
    create_manual_enrollment_audit(reason="invalid json")

    course_enrollment_audit = CourseEnrollmentAudit.objects.first()
    assert course_enrollment_audit.reason == "invalid json"


@pytest.mark.django_db
def test_update_existing_course_enrollment_audit(user, enrollment, create_manual_enrollment_audit):
    """Test updating an existing CourseEnrollmentAudit instance."""
    create_manual_enrollment_audit()

    course_enrollment_audit = CourseEnrollmentAudit.objects.first()
    assert course_enrollment_audit.state_transition == UNENROLLED_TO_ENROLLED

    create_manual_enrollment_audit(state_transition=ENROLLED_TO_UNENROLLED)

    assert CourseEnrollmentAudit.objects.count() == 1

    course_enrollment_audit.refresh_from_db()
    assert course_enrollment_audit.state_transition == ENROLLED_TO_UNENROLLED


@pytest.mark.django_db
def test_create_without_enrollment(user):
    """Test creating a CourseEnrollmentAudit without an associated CourseEnrollment."""
    ManualEnrollmentAudit.objects.create(
        enrolled_email=user.email,
        state_transition=UNENROLLED_TO_ENROLLED,
    )

    course_enrollment_audit = CourseEnrollmentAudit.objects.first()
    # noinspection PyTestUnpassedFixture
    assert course_enrollment_audit.enrollment is None
    assert course_enrollment_audit.user_id is None
    assert course_enrollment_audit.course_id is None
    assert course_enrollment_audit.enrolled_email == user.email
