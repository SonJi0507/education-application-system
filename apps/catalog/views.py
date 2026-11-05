from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render

from apps.catalog.models import Course


def course_list(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        "catalog/course_list.html",
        {"courses": Course.objects.published()},
    )


def course_detail(request: HttpRequest, slug: str) -> HttpResponse:
    course = get_object_or_404(Course.objects.featured(), slug=slug)
    return render(
        request,
        "catalog/landing.html",
        {
            "course": course,
            "can_apply": course.recruitment_status == Course.RecruitmentStatus.OPEN,
        },
    )
