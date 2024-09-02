from django.core.management.base import BaseCommand

from openedx_course_enrollment_audit.models import CourseEnrollmentAudit

ManualEnrollmentAudit = CourseEnrollmentAudit.get_manual_enrollment_audit_model()


class Command(BaseCommand):
    help = 'Backfill CourseEnrollmentAudit from ManualEnrollmentAudit'

    def handle(self, *args, **kwargs):
        total_count = ManualEnrollmentAudit.objects.count()
        self.stdout.write(self.style.NOTICE(f'Starting backfill of {total_count} records from ManualEnrollmentAudit.'))

        batch_size = 10000
        for i, manual_enrollment in enumerate(ManualEnrollmentAudit.objects.all().iterator(), 1):
            CourseEnrollmentAudit.create_from_manual_enrollment(manual_enrollment)

            if i % batch_size == 0:
                self.stdout.write(self.style.SUCCESS(f'Processed {i} records...'))

        self.stdout.write(self.style.SUCCESS('Backfill completed successfully.'))
