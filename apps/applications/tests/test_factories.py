import pytest

from apps.applications.models import Application
from apps.applications.tests.factories import ApplicationFactory


@pytest.mark.django_db
def test_신청_팩토리는_접수_상태의_신청을_만든다():
    # Arrange
    expected_status = Application.Status.RECEIVED

    # Act
    ApplicationFactory(status=expected_status)

    # Assert
    application = Application.objects.get()
    assert application.status == expected_status
    assert application.course_id is not None
