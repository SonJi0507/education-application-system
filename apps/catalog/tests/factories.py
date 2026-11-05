import factory
from factory.django import DjangoModelFactory

from apps.catalog.models import Course, CurriculumItem


class CourseFactory(DjangoModelFactory):
    class Meta:  # ty: ignore[invalid-attribute-override]
        model = Course

    title = factory.Sequence(lambda n: f"교육 {n}")
    slug = factory.Sequence(lambda n: f"course-{n}")
    summary = "한 줄 소개"
    description = "설명"
    is_published = False


class CurriculumItemFactory(DjangoModelFactory):
    class Meta:  # ty: ignore[invalid-attribute-override]
        model = CurriculumItem

    course = factory.SubFactory(CourseFactory)
    position = factory.Sequence(lambda n: n + 1)
    title = "개발 환경"
    body = "설치부터 시작합니다."
