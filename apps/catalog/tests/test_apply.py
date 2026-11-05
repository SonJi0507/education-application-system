import json

import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse

from apps.applications.models import Application
from apps.catalog.models import Course
from apps.catalog.tests.factories import CourseFactory

pytestmark = pytest.mark.django_db


def test_모집중인_교육_상세의_신청_폼은_신청_API로_보낸다(client):
    # Arrange
    CourseFactory(title="파이썬 입문", slug="python-basics", is_published=True)
    course = Course.objects.get(slug="python-basics")

    # Act
    response = client.get(reverse("course-detail", args=["python-basics"]))

    # Assert
    content = response.content.decode()
    assert response.status_code == 200
    assert "수강 신청" in content
    assert f'action="{reverse("application-list")}"' in content
    assert f'name="course" value="{course.pk}"' in content
    assert 'name="name"' in content
    assert 'autocomplete="email"' in content
    assert 'autocomplete="street-address"' in content
    assert 'name="contact_date"' in content
    assert "신청하기" in content
    assert "application-form.js" in content


def test_모집_중이_아니면_신청_폼을_숨긴다(client):
    # Arrange
    CourseFactory(
        slug="later",
        is_published=True,
        recruitment_status=Course.RecruitmentStatus.UPCOMING,
    )
    CourseFactory(
        slug="done",
        is_published=True,
        recruitment_status=Course.RecruitmentStatus.CLOSED,
    )

    # Act
    upcoming = client.get(reverse("course-detail", args=["later"]))
    closed = client.get(reverse("course-detail", args=["done"]))

    # Assert
    upcoming_content = upcoming.content.decode()
    closed_content = closed.content.decode()
    assert "모집 예정입니다" in upcoming_content
    assert 'name="email"' not in upcoming_content
    assert "모집이 마감되어 신청할 수 없습니다." in closed_content
    assert 'name="email"' not in closed_content


def _logged_in_client() -> Client:
    user = User.objects.create_user(username="applicant", password="pass")
    client = Client(enforce_csrf_checks=True, HTTP_HOST="127.0.0.1")
    client.force_login(user)
    return client


def _apply_payload(course: Course) -> dict[str, object]:
    return {
        "course": course.pk,
        "name": "김민아",
        "email": "mina@example.com",
        "address": "서울특별시 마포구 월드컵북로 400",
        "contact_date": "2026-11-20",
    }


def test_로그인한_신청은_쿠키의_CSRF_토큰으로_접수된다():
    # Arrange
    CourseFactory(slug="python-basics", is_published=True)
    course = Course.objects.get(slug="python-basics")
    client = _logged_in_client()
    client.get(reverse("course-detail", args=["python-basics"]))

    # Act
    response = client.post(
        reverse("application-list"),
        data=json.dumps(_apply_payload(course)),
        content_type="application/json",
        HTTP_X_CSRFTOKEN=client.cookies["csrftoken"].value,
    )

    # Assert
    assert response.status_code == 201
    assert Application.objects.get().course_id == course.pk


def test_로그인한_신청의_CSRF_토큰이_다르면_거절된다():
    # Arrange
    CourseFactory(slug="python-basics", is_published=True)
    course = Course.objects.get(slug="python-basics")
    client = _logged_in_client()
    client.get(reverse("course-detail", args=["python-basics"]))

    # Act
    response = client.post(
        reverse("application-list"),
        data=json.dumps(_apply_payload(course)),
        content_type="application/json",
        HTTP_X_CSRFTOKEN="a" * 64,
    )

    # Assert
    assert response.status_code == 403
    assert "CSRF" in response.json()["detail"]
    assert Application.objects.count() == 0


def test_상세_페이지_주소로는_신청이_저장되지_않는다(client):
    # Arrange
    CourseFactory(slug="python-basics", is_published=True)

    # Act
    response = client.post(reverse("course-detail", args=["python-basics"]), {"name": "김민아"})

    # Assert
    assert response.status_code == 200
    assert Application.objects.count() == 0
