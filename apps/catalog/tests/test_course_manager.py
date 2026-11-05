import pytest

from apps.catalog.models import Course
from apps.catalog.models.course import CourseQuerySet
from apps.catalog.tests.factories import CourseFactory, CurriculumItemFactory


@pytest.mark.django_db
def test_공개된_교육_중_가장_먼저_만든_교육을_반환한다():
    # Arrange
    CourseFactory(slug="draft", is_published=False)
    published = CourseFactory(slug="python-basics", is_published=True)
    CourseFactory(slug="web-basics", is_published=True)
    CurriculumItemFactory(course=published, position=1, title="개발 환경")

    # Act
    featured = Course.objects.featured_course()

    # Assert
    assert isinstance(Course.objects.get_queryset(), CourseQuerySet)
    assert featured == published
    assert [item.title for item in featured.curriculum.all()] == ["개발 환경"]


@pytest.mark.django_db
def test_공개된_교육이_없으면_None을_반환한다():
    # Arrange
    CourseFactory(slug="draft", is_published=False)

    # Act
    featured = Course.objects.featured_course()

    # Assert
    assert featured is None


@pytest.mark.django_db
def test_대표_교육은_커리큘럼을_미리_가져온다(django_assert_num_queries):
    # Arrange
    course = CourseFactory(slug="python-basics", is_published=True)
    CurriculumItemFactory(course=course, position=1, title="개발 환경")

    # Act
    featured = Course.objects.featured_course()

    # Assert
    with django_assert_num_queries(0):
        titles = [item.title for item in featured.curriculum.all()]
    assert titles == ["개발 환경"]
