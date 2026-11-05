from dataclasses import dataclass
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.applications.models import Application
from apps.catalog.models import Course, CurriculumItem


@dataclass(frozen=True)
class CurriculumSeed:
    position: int
    title: str
    body: str


@dataclass(frozen=True)
class ApplicationSeed:
    name: str
    email: str
    address: str
    contact_in_days: int
    status: str
    confirmation_sent: bool = False
    contact_notice_sent: bool = False


@dataclass(frozen=True)
class CourseSeed:
    slug: str
    title: str
    summary: str
    description: str
    hero_alt: str
    is_published: bool
    curriculum: tuple[CurriculumSeed, ...]
    applications: tuple[ApplicationSeed, ...]


COURSES = (
    CourseSeed(
        slug="python-basics",
        title="파이썬 입문",
        summary="문법부터 작은 프로그램까지 직접 만드는 입문 과정입니다.",
        description=(
            "변수, 조건, 반복, 함수를 익히고 마지막에 신청 목록을 출력하는 프로그램을 만듭니다."
        ),
        hero_alt="노트북으로 파이썬 코드를 작성하는 수업 장면",
        is_published=True,
        curriculum=(
            CurriculumSeed(
                1, "개발 환경", "파이썬을 설치하고 편집기에서 첫 프로그램을 실행합니다."
            ),
            CurriculumSeed(2, "기본 문법", "변수, 조건문, 반복문으로 입력을 나눠 처리합니다."),
            CurriculumSeed(3, "함수", "신청 정보를 받아 출력하는 함수를 만듭니다."),
        ),
        applications=(
            ApplicationSeed(
                name="김민아",
                email="mina.kim@example.com",
                address="서울특별시 마포구 월드컵북로 400",
                contact_in_days=3,
                status=Application.Status.RECEIVED,
            ),
        ),
    ),
    CourseSeed(
        slug="web-basics",
        title="웹 서비스 기초",
        summary="소개 페이지와 신청 폼을 갖춘 웹 서비스를 만듭니다.",
        description="HTML로 교육 소개를 구성하고, Django로 신청을 저장하고 상태를 바꿉니다.",
        hero_alt="화면에 교육 소개 페이지가 열려 있는 수업 장면",
        is_published=True,
        curriculum=(
            CurriculumSeed(
                1, "페이지 구성", "교육명, 한 줄 소개, 커리큘럼이 보이는 페이지를 만듭니다."
            ),
            CurriculumSeed(2, "신청 폼", "이름, 이메일, 주소, 연락 가능 날짜를 받습니다."),
            CurriculumSeed(3, "신청 관리", "접수, 확인중, 완료 상태를 구분합니다."),
        ),
        applications=(
            ApplicationSeed(
                name="이서준",
                email="seojoon.lee@example.com",
                address="경기도 성남시 분당구 판교역로 235",
                contact_in_days=5,
                status=Application.Status.REVIEWING,
                confirmation_sent=True,
            ),
            ApplicationSeed(
                name="박하은",
                email="haeun.park@example.com",
                address="부산광역시 해운대구 센텀중앙로 79",
                contact_in_days=1,
                status=Application.Status.COMPLETED,
                confirmation_sent=True,
                contact_notice_sent=True,
            ),
        ),
    ),
)


class Command(BaseCommand):
    help = "교육, 커리큘럼, 신청 테스트 데이터를 넣습니다. 같은 데이터는 다시 만들지 않습니다."

    @transaction.atomic
    def handle(self, *args, **options):
        today = timezone.localdate()
        now = timezone.now()
        for course_seed in COURSES:
            course, _ = Course.objects.update_or_create(
                slug=course_seed.slug,
                defaults={
                    "title": course_seed.title,
                    "summary": course_seed.summary,
                    "description": course_seed.description,
                    "hero_alt": course_seed.hero_alt,
                    "is_published": course_seed.is_published,
                },
            )
            for item in course_seed.curriculum:
                CurriculumItem.objects.update_or_create(
                    course=course,
                    position=item.position,
                    defaults={"title": item.title, "body": item.body},
                )
            for application in course_seed.applications:
                Application.objects.get_or_create(
                    course=course,
                    email=application.email,
                    defaults={
                        "name": application.name,
                        "address": application.address,
                        "contact_date": today + timedelta(days=application.contact_in_days),
                        "status": application.status,
                        "confirmation_sent_at": now if application.confirmation_sent else None,
                        "contact_notice_sent_at": now if application.contact_notice_sent else None,
                    },
                )

        slugs = [course.slug for course in COURSES]
        course_count = Course.objects.filter(slug__in=slugs).count()
        curriculum_count = CurriculumItem.objects.filter(course__slug__in=slugs).count()
        application_count = Application.objects.filter(course__slug__in=slugs).count()
        self.stdout.write(
            self.style.SUCCESS(
                f"시드 데이터를 넣었습니다. 교육 {course_count}건, "
                f"커리큘럼 {curriculum_count}건, 신청 {application_count}건."
            )
        )
