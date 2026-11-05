import io
from datetime import date

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from PIL import Image

from apps.catalog.models import Course
from apps.catalog.tests.factories import CourseFactory, CurriculumItemFactory


def hero_image() -> SimpleUploadedFile:
    buffer = io.BytesIO()
    Image.new("RGB", (16, 9), (15, 110, 86)).save(buffer, format="PNG")
    return SimpleUploadedFile("hero.png", buffer.getvalue(), content_type="image/png")


@pytest.mark.django_db
def test_교육_목록에_모집_상태와_기간을_보여준다(client):
    # Arrange
    CourseFactory(title="비공개 교육", slug="draft", is_published=False)
    CourseFactory(
        title="파이썬 입문",
        slug="python-basics",
        summary="문법부터 작은 프로그램까지 만듭니다.",
        is_published=True,
        recruitment_status=Course.RecruitmentStatus.OPEN,
        starts_on=date(2026, 11, 2),
        ends_on=date(2026, 12, 18),
    )
    CourseFactory(
        title="웹 서비스 기초",
        slug="web-basics",
        summary="소개 페이지와 신청 폼을 만듭니다.",
        is_published=True,
        recruitment_status=Course.RecruitmentStatus.UPCOMING,
        starts_on=date(2027, 1, 5),
        ends_on=date(2027, 2, 13),
    )

    # Act
    response = client.get(reverse("course-list"))

    # Assert
    content = response.content.decode()
    assert response.status_code == 200
    assert "파이썬 입문" in content
    assert "웹 서비스 기초" in content
    assert "모집중" in content
    assert "모집 예정" in content
    assert "2026.11.02 ~ 2026.12.18" in content
    assert "2027.01.05 ~ 2027.02.13" in content
    assert reverse("course-detail", args=["python-basics"]) in content
    assert "비공개 교육" not in content


@pytest.mark.django_db
def test_공개된_교육이_없으면_목록에_안내_문구를_보여준다(client):
    # Arrange
    CourseFactory(is_published=False)

    # Act
    response = client.get(reverse("course-list"))

    # Assert
    assert response.status_code == 200
    assert "공개된 교육이 없습니다" in response.content.decode()


@pytest.mark.django_db
def test_교육_상세에_소개와_커리큘럼을_보여준다(client):
    # Arrange
    course = CourseFactory(
        title="파이썬 입문",
        slug="python-basics",
        summary="문법부터 작은 프로그램까지 만듭니다.",
        description="마지막에 신청 목록을 출력합니다.",
        is_published=True,
        recruitment_status=Course.RecruitmentStatus.OPEN,
        starts_on=date(2026, 11, 2),
        ends_on=date(2026, 12, 18),
    )
    CurriculumItemFactory(course=course, position=1, title="개발 환경", body="파이썬을 설치합니다.")
    CourseFactory(title="나중 교육", slug="later", is_published=True)

    # Act
    response = client.get(reverse("course-detail", args=["python-basics"]))

    # Assert
    content = response.content.decode()
    assert response.status_code == 200
    assert "파이썬 입문" in content
    assert "문법부터 작은 프로그램까지 만듭니다." in content
    assert "마지막에 신청 목록을 출력합니다." in content
    assert "개발 환경" in content
    assert "파이썬을 설치합니다." in content
    assert "2026.11.02 ~ 2026.12.18" in content
    assert "모집중" in content
    assert "나중 교육" not in content


@pytest.mark.django_db
def test_공개되지_않은_교육_상세는_열_수_없다(client):
    # Arrange
    CourseFactory(slug="draft", is_published=False)

    # Act
    response = client.get(reverse("course-detail", args=["draft"]))

    # Assert
    assert response.status_code == 404


@pytest.mark.django_db
def test_대표_이미지는_먼저_불러오고_설명을_붙인다(client):
    # Arrange
    CourseFactory(
        title="파이썬 입문",
        slug="python-basics",
        is_published=True,
        hero_image=hero_image(),
        hero_alt="노트북으로 코드를 작성하는 수업 장면",
    )
    course = Course.objects.get(slug="python-basics")

    # Act
    response = client.get(reverse("course-detail", args=["python-basics"]))

    # Assert
    content = response.content.decode()
    assert response.status_code == 200
    assert course.hero_image.url in content
    assert 'alt="노트북으로 코드를 작성하는 수업 장면"' in content
    assert 'fetchpriority="high"' in content
    assert "loading=" not in content
