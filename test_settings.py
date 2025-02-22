"""
These settings are here to use during tests, because django requires them.

In a real-world use case, apps in this project are installed into other
Django applications, so these settings will not be used.
"""

INSTALLED_APPS = (
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "openedx_course_enrollment_audit",
)

TEST_OPENEDX_COURSE_ENROLLMENT_AUDIT = True
USE_TZ = True
