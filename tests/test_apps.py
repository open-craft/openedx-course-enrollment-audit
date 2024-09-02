"""Test Django application initialization and its configuration."""

from django.apps import apps


def test_app():
    """
    Check that the app is detected by Django.
    Verify the Open edX plugin config structure.
    """
    app = apps.get_app_config("openedx_course_enrollment_audit")

    assert app.name == "openedx_course_enrollment_audit"
    print(app.plugin_app)
    assert app.plugin_app["signals_config"]["lms.djangoapp"]["relative_path"] == "signals"
