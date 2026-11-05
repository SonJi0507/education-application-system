from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from apps.applications.models import Application


def send_confirmation(application: Application) -> None:
    send_mail(
        subject=f"[교육 신청] {application.course.title} 접수가 완료되었습니다",
        message=(
            f"{application.name}님, {application.course.title} 신청이 접수되었습니다.\n"
            f"연락 가능 날짜는 {application.contact_date:%Y-%m-%d}입니다."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[application.email],
        fail_silently=False,
    )
    application.confirmation_sent_at = timezone.now()
    application.save(update_fields=["confirmation_sent_at", "updated_at"])


def send_contact_notice(application: Application) -> None:
    send_mail(
        subject=f"[교육 신청] {application.course.title} 연락 안내",
        message=(
            f"{application.name}님, 오늘({application.contact_date:%Y-%m-%d})은 "
            f"{application.course.title} 연락 가능 날짜입니다."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[application.email],
        fail_silently=False,
    )
    application.contact_notice_sent_at = timezone.now()
    application.save(update_fields=["contact_notice_sent_at", "updated_at"])
