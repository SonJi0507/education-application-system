from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.applications.mail import send_contact_notice
from apps.applications.models import Application


class Command(BaseCommand):
    help = "연락 가능 날짜가 된 신청에 안내 메일을 보냅니다. 이미 보낸 신청은 다시 보내지 않습니다."

    def handle(self, *args: object, **options: object) -> None:
        applications = Application.objects.due_for_contact_notice(
            timezone.localdate()
        ).select_related("course")
        sent = 0
        for application in applications:
            send_contact_notice(application)
            sent += 1
        self.stdout.write(self.style.SUCCESS(f"안내 메일 {sent}건을 보냈습니다."))
