from __future__ import annotations

from typing import TYPE_CHECKING, Self

from django.core.exceptions import ValidationError
from django.db import models

from apps.common.models import TimeMixinModel

if TYPE_CHECKING:
    from django.db.models.fields.related_descriptors import RelatedManager

    from apps.catalog.models.curriculum_item import CurriculumItem


class CourseQuerySet(models.QuerySet["Course"]):
    def published(self) -> Self:
        return self.filter(is_published=True).order_by("starts_on", "id")

    def featured(self) -> Self:
        return self.published().prefetch_related("curriculum")


class CourseManager(models.Manager["Course"]):
    def get_queryset(self) -> CourseQuerySet:
        return CourseQuerySet(self.model, using=self._db)

    def published(self) -> CourseQuerySet:
        return self.get_queryset().published()

    def featured(self) -> CourseQuerySet:
        return self.get_queryset().featured()

    def featured_course(self) -> Course | None:
        return self.featured().order_by("id").first()


class Course(TimeMixinModel):
    class RecruitmentStatus(models.TextChoices):
        UPCOMING = "upcoming", "모집 예정"
        OPEN = "open", "모집중"
        CLOSED = "closed", "모집 마감"

    title = models.CharField("교육명", max_length=120)
    slug = models.SlugField("슬러그", unique=True)
    summary = models.CharField("한 줄 소개", max_length=200)
    description = models.TextField("설명")
    hero_image = models.ImageField("대표 이미지", upload_to="courses/", blank=True)
    hero_alt = models.CharField("대표 이미지 설명", max_length=200, blank=True)
    recruitment_status = models.CharField(
        "모집 상태",
        max_length=20,
        choices=RecruitmentStatus.choices,
        default=RecruitmentStatus.OPEN,
    )
    starts_on = models.DateField("교육 시작일", null=True, blank=True)
    ends_on = models.DateField("교육 종료일", null=True, blank=True)
    is_published = models.BooleanField("공개", default=False)
    curriculum: RelatedManager[CurriculumItem]

    objects = CourseManager()

    class Meta:
        verbose_name = "교육"
        verbose_name_plural = "교육"
        ordering = ("id",)

    def __str__(self):
        return self.title

    def clean(self) -> None:
        super().clean()
        if self.starts_on and self.ends_on and self.ends_on < self.starts_on:
            raise ValidationError({"ends_on": "교육 종료일은 시작일 이후여야 합니다."})

    def period_label(self) -> str:
        if self.starts_on and self.ends_on:
            return f"{self.starts_on:%Y.%m.%d} ~ {self.ends_on:%Y.%m.%d}"
        return "기간 미정"
