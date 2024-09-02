from django.core.management.base import BaseCommand

from openedx_course_enrollment_audit.models import CourseEnrollmentAudit

ManualEnrollmentAudit = CourseEnrollmentAudit.get_manual_enrollment_audit_model()


class Command(BaseCommand):
    help = 'Backfill CourseEnrollmentAudit from ManualEnrollmentAudit'

    def handle(self, *args, **kwargs):
        total_count = ManualEnrollmentAudit.objects.count()
        self.stdout.write(self.style.NOTICE(f'Starting backfill of {total_count} records from ManualEnrollmentAudit.'))

        for manual_enrollment in ManualEnrollmentAudit.objects.all().iterator():
            course_enrollment_audit, created = CourseEnrollmentAudit.create_from_manual_enrollment(manual_enrollment)

            if created:
                self.stdout.write(self.style.SUCCESS(
                    f'Created new CourseEnrollmentAudit for email: {manual_enrollment.enrolled_email}, course_id: {course_enrollment_audit.course_id}.'))
            else:
                self.stdout.write(self.style.WARNING(
                    f'Updated existing CourseEnrollmentAudit for email: {manual_enrollment.enrolled_email}, course_id: {course_enrollment_audit.course_id}.'))

        self.stdout.write(self.style.SUCCESS('Backfill completed successfully.'))
