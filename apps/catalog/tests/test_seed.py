import pytest
from django.core.management import call_command

from apps.applications.models import Application
from apps.catalog.management.commands.seed import COURSES
from apps.catalog.models import Course, CurriculumItem


@pytest.mark.django_db
def test_시드는_교육_커리큘럼_신청을_한_번씩만_넣는다():
    # Arrange
    slugs = [course.slug for course in COURSES]

    # Act
    call_command("seed")
    call_command("seed")

    # Assert
    assert Course.objects.filter(slug__in=slugs).count() == len(COURSES)
    assert CurriculumItem.objects.filter(course__slug__in=slugs).count() == sum(
        len(course.curriculum) for course in COURSES
    )
    assert Application.objects.filter(course__slug__in=slugs).count() == sum(
        len(course.applications) for course in COURSES
    )
    assert set(Application.objects.values_list("status", flat=True)) == {
        Application.Status.RECEIVED,
        Application.Status.REVIEWING,
        Application.Status.COMPLETED,
    }
