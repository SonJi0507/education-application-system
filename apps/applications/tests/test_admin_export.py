import csv
import io
from datetime import date

import pytest
from django.urls import reverse

from apps.applications.models import Application
from apps.applications.tests.factories import ApplicationFactory

pytestmark = pytest.mark.django_db


def test_선택한_신청만_CSV로_내보낸다(admin_user, client):
    # Arrange
    client.force_login(admin_user)
    ApplicationFactory(
        name="김민아",
        email="mina@example.com",
        address="서울, 마포구",
        contact_date=date(2026, 11, 20),
        status=Application.Status.RECEIVED,
        course__title="파이썬 입문",
    )
    ApplicationFactory(name="이서준", email="seo@example.com")
    selected = Application.objects.get(email="mina@example.com")

    # Act
    response = client.post(
        reverse("admin:applications_application_changelist"),
        {"action": "export_applications_csv", "_selected_action": [selected.pk]},
    )

    # Assert
    assert response.status_code == 200
    assert response["Content-Type"].startswith("text/csv")
    assert "attachment;" in response["Content-Disposition"]
    rows = list(csv.reader(io.StringIO(response.content.decode("utf-8-sig"))))
    assert rows[0] == ["이름", "이메일", "주소", "교육", "연락 가능 날짜", "상태", "접수 시각"]
    assert rows[1][0] == "김민아"
    assert rows[1][1] == "mina@example.com"
    assert rows[1][2] == "서울, 마포구"
    assert rows[1][3] == "파이썬 입문"
    assert rows[1][4] == "2026-11-20"
    assert rows[1][5] == "접수"
    assert len(rows) == 2
    assert "이서준" not in response.content.decode("utf-8-sig")


def test_관리자가_아니면_신청_CSV를_받을_수_없다(client):
    # Arrange
    ApplicationFactory()

    # Act
    response = client.post(
        reverse("admin:applications_application_changelist"),
        {"action": "export_applications_csv", "_selected_action": ["1"]},
    )

    # Assert
    assert response.status_code == 302
    assert "text/csv" not in response.get("Content-Type", "")
