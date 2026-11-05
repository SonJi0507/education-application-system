from django.contrib import admin

from apps.catalog.models import Course, CurriculumItem


class CurriculumItemInline(admin.TabularInline):
    model = CurriculumItem
    extra = 1


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "is_published", "updated_at")
    list_filter = ("is_published",)
    search_fields = ("title", "summary")
    inlines = (CurriculumItemInline,)
