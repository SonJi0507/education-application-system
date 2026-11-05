from rest_framework import serializers

from apps.applications.models import Application
from apps.catalog.models import Course


class ApplicationCreateSerializer(serializers.ModelSerializer[Application]):
    course = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.filter(is_published=True),
        error_messages={
            "required": "교육을 선택해 주세요.",
            "does_not_exist": "신청할 수 없는 교육입니다.",
            "incorrect_type": "교육을 선택해 주세요.",
        },
    )
    name = serializers.CharField(
        max_length=100,
        error_messages={"required": "이름을 입력해 주세요.", "blank": "이름을 입력해 주세요."},
    )
    email = serializers.EmailField(
        error_messages={
            "required": "이메일을 입력해 주세요.",
            "blank": "이메일을 입력해 주세요.",
            "invalid": "이메일 형식이 올바르지 않습니다.",
        },
    )
    address = serializers.CharField(
        error_messages={"required": "주소를 입력해 주세요.", "blank": "주소를 입력해 주세요."},
    )
    contact_date = serializers.DateField(
        error_messages={
            "required": "연락 가능 날짜를 입력해 주세요.",
            "invalid": "연락 가능 날짜 형식이 올바르지 않습니다.",
        },
    )

    class Meta:  # ty: ignore[invalid-attribute-override]
        model = Application
        fields = ("id", "course", "name", "email", "address", "contact_date", "status")
        read_only_fields = ("id", "status")


class ApplicationStaffSerializer(serializers.ModelSerializer[Application]):
    course_title = serializers.CharField(source="course.title", read_only=True)

    class Meta:  # ty: ignore[invalid-attribute-override]
        model = Application
        fields = (
            "id",
            "course",
            "course_title",
            "name",
            "email",
            "address",
            "contact_date",
            "status",
            "confirmation_sent_at",
            "contact_notice_sent_at",
            "created_at",
        )
        read_only_fields = fields
