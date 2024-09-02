"""
This module contains the CourseEnrollmentAudit model, which is used to store parsed and summarized manual enrollment
audit data.
"""

import json
from json import JSONDecodeError

from django.apps import apps
from django.contrib.auth.models import User
from django.db import models


class CourseEnrollmentAudit(models.Model):
    """
    Table for storing parsed and summarized manual enrollment audit data.
    This model syncs with ManualEnrollmentAudit to keep track of enrollment changes.

    .. pii: Contains enrolled_email, retired in LMSAccountRetirementView.
    .. pii_types: email
    .. pii_retirement: local_api
    """

    manual_enrollment_audit = models.OneToOneField('student.ManualEnrollmentAudit',
                                                   on_delete=models.CASCADE, related_name='course_enrollment_audit')
    enrollment = models.ForeignKey('student.CourseEnrollment', null=True, on_delete=models.CASCADE)
    enrolled_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    enrolled_email = models.CharField(max_length=255, db_index=True)
    time_stamp = models.DateTimeField(auto_now_add=True, null=True)
    state_transition = models.CharField(max_length=255)
    org = models.CharField(max_length=255, null=True, blank=True)
    course_id = models.CharField(max_length=255, null=True, blank=True)
    role = models.CharField(blank=True, null=True, max_length=64)
    reason = models.TextField(null=True, blank=True)
    user_id = models.IntegerField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['enrolled_email', 'course_id'], name='unique_email_course')
        ]

    @classmethod
    def get_manual_enrollment_audit_model(cls):  # pragma: no cover
        """
        Dynamically get the ManualEnrollmentAudit model.
        """
        return apps.get_model('student', 'ManualEnrollmentAudit')

    @classmethod
    def get_course_enrollment_model(cls):  # pragma: no cover
        """
        Dynamically get the CourseEnrollment model.
        """
        return apps.get_model('student', 'CourseEnrollment')

    @classmethod
    def create_from_manual_enrollment(cls, manual_enrollment):
        """
        Create or update a CourseEnrollmentAudit instance based on the provided ManualEnrollmentAudit instance.
        """
        org = None
        course_id = str(manual_enrollment.enrollment.course_id) if manual_enrollment.enrollment else None
        parsed_role = None
        parsed_reason = None

        if manual_enrollment.reason:
            try:
                parsed_data = json.loads(manual_enrollment.reason)
                org = parsed_data.get('org')
                course_id = parsed_data.get('course_id', course_id)
                parsed_role = parsed_data.get('role')
                parsed_reason = parsed_data.get('reason')
            except JSONDecodeError:
                # If the reason field is not a valid JSON, store it as is.
                parsed_reason = manual_enrollment.reason

        return cls.objects.update_or_create(
            enrolled_email=manual_enrollment.enrolled_email,
            course_id=course_id,
            defaults={
                'manual_enrollment_audit': manual_enrollment,
                'enrollment': manual_enrollment.enrollment,
                'enrolled_by': manual_enrollment.enrolled_by,
                'state_transition': manual_enrollment.state_transition,
                'org': org,
                'role': parsed_role or manual_enrollment.role,
                'reason': parsed_reason,
                'user_id': manual_enrollment.enrollment.user_id if manual_enrollment.enrollment else None,
                'time_stamp': manual_enrollment.time_stamp,
            }
        )
