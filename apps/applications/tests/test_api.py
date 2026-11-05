from datetime import timedelta

import pytest
from django.core import mail
from django.core.management import call_command
from django.utils import timezone
from rest_framework.test import APIClient

from apps.applications.models import Application
from apps.applications.tests.factories import ApplicationFactory
from apps.catalog.tests.factories import CourseFactory

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def locmem_email(settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    from django.core.mail.backends.locmem import EmailBackend

    EmailBackend()
    mail.outbox.clear()


def application_payload(course, **overrides):
    payload = {
        "course": course.pk,
        "name": "김민아",
        "email": "mina@example.com",
        "address": "서울특별시 마포구 월드컵북로 400",
        "contact_date": "2026-11-20",
    }
    payload.update(overrides)
    return payload


def test_신청을_접수하면_저장하고_확인_메일을_보낸다():
    # Arrange
    mail.outbox.clear()
    course = CourseFactory(title="파이썬 입문", is_published=True)
    client = APIClient()

    # Act
    response = client.post("/api/applications/", application_payload(course), format="json")

    # Assert
    assert response.status_code == 201
    application = Application.objects.get()
    assert application.course == course
    assert application.name == "김민아"
    assert application.status == Application.Status.RECEIVED
    assert application.confirmation_sent_at is not None
    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == ["mina@example.com"]
    assert "파이썬 입문" in mail.outbox[0].subject


def test_공개되지_않은_교육에는_신청할_수_없다():
    # Arrange
    course = CourseFactory(is_published=False)
    client = APIClient()

    # Act
    response = client.post("/api/applications/", application_payload(course), format="json")

    # Assert
    assert response.status_code == 400
    assert response.json()["course"] == ["신청할 수 없는 교육입니다."]
    assert Application.objects.count() == 0


def test_이름이_없으면_신청이_거절된다():
    # Arrange
    course = CourseFactory(is_published=True)
    client = APIClient()

    # Act
    response = client.post(
        "/api/applications/",
        application_payload(course, name=""),
        format="json",
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["name"] == ["이름을 입력해 주세요."]


def test_관리자는_신청_목록을_조회한다(admin_user):
    # Arrange
    ApplicationFactory(name="김민아", email="mina@example.com")
    application = Application.objects.get(email="mina@example.com")
    client = APIClient()
    client.force_authenticate(user=admin_user)

    # Act
    response = client.get("/api/applications/")

    # Assert
    assert response.status_code == 200
    body = response.json()
    assert body["count"] == 1
    assert body["results"][0]["id"] == application.pk
    assert body["results"][0]["course_title"] == application.course.title


def test_로그인하지_않으면_신청_목록을_볼_수_없다():
    # Arrange
    ApplicationFactory()
    client = APIClient()

    # Act
    response = client.get("/api/applications/")

    # Assert
    assert response.status_code == 403


def test_관리자는_상태와_검색어로_신청을_거른다(admin_user):
    # Arrange
    ApplicationFactory(name="김민아", email="mina@example.com", status=Application.Status.RECEIVED)
    ApplicationFactory(
        name="김민아",
        email="mina2@example.com",
        status=Application.Status.REVIEWING,
    )
    ApplicationFactory(name="박하은", email="haeun@example.com", status=Application.Status.RECEIVED)
    matched = Application.objects.get(email="mina@example.com")
    client = APIClient()
    client.force_authenticate(user=admin_user)

    # Act
    response = client.get(
        "/api/applications/", {"status": Application.Status.RECEIVED, "q": "민아"}
    )

    # Assert
    assert response.status_code == 200
    assert [item["id"] for item in response.json()["results"]] == [matched.pk]


def test_관리자는_신청_한_건을_조회한다(admin_user):
    # Arrange
    ApplicationFactory(email="mina@example.com")
    application = Application.objects.get(email="mina@example.com")
    client = APIClient()
    client.force_authenticate(user=admin_user)

    # Act
    response = client.get(f"/api/applications/{application.pk}/")

    # Assert
    assert response.status_code == 200
    assert response.json()["email"] == application.email


def test_연락_가능_날짜가_된_신청에만_안내_메일을_보낸다():
    # Arrange
    mail.outbox.clear()
    today = timezone.localdate()
    ApplicationFactory(contact_date=today, email="due@example.com")
    ApplicationFactory(contact_date=today + timedelta(days=1), email="later@example.com")
    ApplicationFactory(
        contact_date=today - timedelta(days=1),
        email="sent@example.com",
        contact_notice_sent_at=timezone.now(),
    )

    # Act
    call_command("send_contact_notices")

    # Assert
    due = Application.objects.get(email="due@example.com")
    already_sent = Application.objects.get(email="sent@example.com")
    assert due.contact_notice_sent_at is not None
    assert already_sent.contact_notice_sent_at is not None
    assert [item.to for item in mail.outbox] == [["due@example.com"]]
