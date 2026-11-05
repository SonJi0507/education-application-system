from django.contrib import admin

from apps.applications.models import Application


@admin.action(description="선택 신청을 확인중으로 변경")
def mark_reviewing(modeladmin, request, queryset):
    queryset.update(status=Application.Status.REVIEWING)


@admin.action(description="선택 신청을 완료로 변경")
def mark_completed(modeladmin, request, queryset):
    queryset.update(status=Application.Status.COMPLETED)


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "email", "course", "contact_date", "status", "created_at")
    list_filter = ("status", "contact_date", "course")
    search_fields = ("name", "email")
    readonly_fields = ("confirmation_sent_at", "contact_notice_sent_at", "created_at", "updated_at")
    actions = (mark_reviewing, mark_completed)
