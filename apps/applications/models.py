from datetime import date
from typing import Self

from django.db import models
from django.db.models import Q

from apps.common.models import TimeMixinModel


class ApplicationQuerySet(models.QuerySet["Application"]):
    def filtered(self, status: str = "", query: str = "") -> Self:
        queryset = self
        if status in Application.Status.values:
            queryset = queryset.filter(status=status)
        cleaned = query.strip()
        if cleaned:
            queryset = queryset.filter(Q(name__icontains=cleaned) | Q(email__icontains=cleaned))
        return queryset

    def due_for_contact_notice(self, today: date) -> Self:
        return self.filter(contact_date__lte=today, contact_notice_sent_at__isnull=True)


class ApplicationManager(models.Manager["Application"]):
    def get_queryset(self) -> ApplicationQuerySet:
        return ApplicationQuerySet(self.model, using=self._db)

    def filtered(self, status: str = "", query: str = "") -> ApplicationQuerySet:
        return self.get_queryset().filtered(status=status, query=query)

    def due_for_contact_notice(self, today: date) -> ApplicationQuerySet:
        return self.get_queryset().due_for_contact_notice(today)


class Application(TimeMixinModel):
    class Status(models.TextChoices):
        RECEIVED = "received", "접수"
        REVIEWING = "reviewing", "확인중"
        COMPLETED = "completed", "완료"

    course = models.ForeignKey(
        "catalog.Course",
        verbose_name="교육",
        related_name="applications",
        on_delete=models.PROTECT,
    )
    name = models.CharField("이름", max_length=100)
    email = models.EmailField("이메일")
    address = models.TextField("주소")
    contact_date = models.DateField("연락 가능 날짜")
    status = models.CharField(
        "상태",
        max_length=20,
        choices=Status.choices,
        default=Status.RECEIVED,
    )
    confirmation_sent_at = models.DateTimeField("접수 확인 메일 시각", null=True, blank=True)
    contact_notice_sent_at = models.DateTimeField("연락 안내 메일 시각", null=True, blank=True)

    objects = ApplicationManager()

    class Meta:
        verbose_name = "신청"
        verbose_name_plural = "신청"
        ordering = ("-created_at",)
        indexes = (
            models.Index(fields=["contact_date", "status"], name="application_contact_status"),
        )

    def __str__(self):
        return f"{self.name} · {self.email}"
