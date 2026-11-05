import factory
from django.utils import timezone
from factory.django import DjangoModelFactory

from apps.applications.models import Application
from apps.catalog.tests.factories import CourseFactory


class ApplicationFactory(DjangoModelFactory):
    class Meta:  # ty: ignore[invalid-attribute-override]
        model = Application

    course = factory.SubFactory(CourseFactory)
    name = "김민아"
    email = factory.Sequence(lambda n: f"student-{n}@example.com")
    address = "서울특별시 마포구 월드컵북로 400"
    contact_date = factory.LazyFunction(timezone.localdate)
    status = Application.Status.RECEIVED
