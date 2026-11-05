from django.conf.urls.static import static
from django.contrib import admin
from django.urls import URLPattern, URLResolver, include, path

from apps.catalog.views import course_detail, course_list
from configs import settings

admin.site.site_header = "교육 신청 관리"
admin.site.site_title = "교육 신청"
admin.site.index_title = "교육과 신청"

urlpatterns: list[URLPattern | URLResolver] = [
    path("", course_list, name="course-list"),
    path("courses/<slug:slug>/", course_detail, name="course-detail"),
    path("admin/", admin.site.urls),
    path("api/", include("apps.applications.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if "debug_toolbar" in settings.INSTALLED_APPS:
    from debug_toolbar.toolbar import debug_toolbar_urls

    urlpatterns += debug_toolbar_urls()
