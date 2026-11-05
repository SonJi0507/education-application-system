from django.contrib import admin

from apps.catalog.models import Course, CurriculumItem


class CurriculumItemInline(admin.TabularInline):
    model = CurriculumItem
    extra = 1


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "recruitment_status", "starts_on", "ends_on", "is_published")
    list_filter = ("is_published", "recruitment_status")
    search_fields = ("title", "summary")
    inlines = (CurriculumItemInline,)
