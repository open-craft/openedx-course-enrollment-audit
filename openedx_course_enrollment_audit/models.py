"""This module contains the model, which is used to store parsed and summarized manual enrollment audit data."""

import json
from json import JSONDecodeError

from django.contrib.auth.models import User
from django.db import models


class CourseEnrollmentAudit(models.Model):  # noqa: DJ008
    """
    Table for storing parsed and summarized manual enrollment audit data.

    This model syncs with ManualEnrollmentAudit to keep track of enrollment changes.

    .. pii: Contains enrolled_email, retired in LMSAccountRetirementView.
    .. pii_types: email_address
    .. pii_retirement: local_api
    """

    manual_enrollment_audit = models.OneToOneField(
        "student.ManualEnrollmentAudit",
        on_delete=models.CASCADE,
        related_name="course_enrollment_audit",
    )
    enrollment = models.ForeignKey("student.CourseEnrollment", null=True, on_delete=models.CASCADE)
    enrolled_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    enrolled_email = models.CharField(max_length=255, db_index=True)
    time_stamp = models.DateTimeField(null=True)
    state_transition = models.CharField(max_length=255)
    org = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    course_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    role = models.CharField(blank=True, null=True, max_length=64)
    reason = models.TextField(null=True, blank=True)
    user_id = models.IntegerField(null=True, blank=True)

    class Meta:  # noqa: D106
        constraints = (models.UniqueConstraint(fields=["enrolled_email", "course_id"], name="unique_email_course"),)

    @classmethod
    def create_from_manual_enrollment(cls, manual_enrollment):  # noqa: ANN001
        """Create or update a CourseEnrollmentAudit instance based on the provided ManualEnrollmentAudit instance."""
        org = None
        course_id = str(manual_enrollment.enrollment.course_id) if manual_enrollment.enrollment else None
        role = manual_enrollment.role

        try:
            parsed_data = json.loads(manual_enrollment.reason)
            org = parsed_data.get("org")
            course_id = parsed_data.get("course_id", course_id)
            role = parsed_data.get("role", role)
            reason = parsed_data.get("reason")
        except (JSONDecodeError, TypeError):
            # If the reason field is not a valid JSON, store it as is.
            reason = manual_enrollment.reason

        cls.objects.update_or_create(
            enrolled_email=manual_enrollment.enrolled_email,
            course_id=course_id,
            defaults={
                "manual_enrollment_audit": manual_enrollment,
                "enrollment": manual_enrollment.enrollment,
                "enrolled_by": manual_enrollment.enrolled_by,
                "state_transition": manual_enrollment.state_transition,
                "org": org,
                "role": role,
                "reason": reason,
                "user_id": manual_enrollment.enrollment.user_id if manual_enrollment.enrollment else None,
                "time_stamp": manual_enrollment.time_stamp,
            },
        )
