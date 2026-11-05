import csv

from django.contrib import admin
from django.http import HttpResponse
from django.utils import timezone

from apps.applications.models import Application


@admin.action(description="선택 신청을 확인중으로 변경")
def mark_reviewing(modeladmin, request, queryset):
    queryset.update(status=Application.Status.REVIEWING)


@admin.action(description="선택 신청을 완료로 변경")
def mark_completed(modeladmin, request, queryset):
    queryset.update(status=Application.Status.COMPLETED)


@admin.action(description="선택한 신청을 CSV로 내보내기")
def export_applications_csv(modeladmin, request, queryset) -> HttpResponse:
    del modeladmin, request
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="applications.csv"'
    response.write("\ufeff")
    writer = csv.writer(response)
    writer.writerow(["이름", "이메일", "주소", "교육", "연락 가능 날짜", "상태", "접수 시각"])
    applications = queryset.select_related("course").order_by("-created_at", "-id")
    for application in applications:
        created_at = timezone.localtime(application.created_at)
        writer.writerow(
            [
                application.name,
                application.email,
                application.address,
                application.course.title,
                application.contact_date.isoformat(),
                application.get_status_display(),
                created_at.strftime("%Y-%m-%d %H:%M"),
            ]
        )
    return response


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "email", "course", "contact_date", "status", "created_at")
    list_filter = ("status", "contact_date", "course")
    search_fields = ("name", "email")
    readonly_fields = ("confirmation_sent_at", "contact_notice_sent_at", "created_at", "updated_at")
    actions = (mark_reviewing, mark_completed, export_applications_csv)
