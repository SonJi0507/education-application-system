import pytest

from apps.applications.models import Application, ApplicationQuerySet
from apps.applications.tests.factories import ApplicationFactory


@pytest.mark.django_db
def test_상태값으로_신청을_거른다():
    # Arrange
    received = ApplicationFactory(status=Application.Status.RECEIVED)
    ApplicationFactory(status=Application.Status.REVIEWING)

    # Act
    matched = list(Application.objects.filtered(status=Application.Status.RECEIVED))

    # Assert
    assert isinstance(Application.objects.get_queryset(), ApplicationQuerySet)
    assert matched == [received]


@pytest.mark.django_db
def test_없는_상태는_거르지_않는다():
    # Arrange
    application = ApplicationFactory(status=Application.Status.RECEIVED)

    # Act
    matched = list(Application.objects.filtered(status="missing"))

    # Assert
    assert matched == [application]


@pytest.mark.django_db
def test_이름이나_이메일에_검색어가_있으면_거른다():
    # Arrange
    by_name = ApplicationFactory(name="김민아", email="mina@example.com")
    by_email = ApplicationFactory(name="이서준", email="MINA.lee@example.com")
    ApplicationFactory(name="박하은", email="haeun@example.com")

    # Act
    matched = set(Application.objects.filtered(query="  mina "))

    # Assert
    assert matched == {by_name, by_email}


@pytest.mark.django_db
def test_교육과_함께_조회한_뒤에도_이어서_거른다():
    # Arrange
    received = ApplicationFactory(status=Application.Status.RECEIVED)
    ApplicationFactory(status=Application.Status.COMPLETED)

    # Act
    matched = list(
        Application.objects.get_queryset()
        .select_related("course")
        .filtered(status=Application.Status.RECEIVED)
    )

    # Assert
    assert matched == [received]
    assert matched[0].course.slug
