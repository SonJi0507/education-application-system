from __future__ import annotations

from typing import TYPE_CHECKING, Self

from django.db import models

from apps.common.models import TimeMixinModel

if TYPE_CHECKING:
    from django.db.models.fields.related_descriptors import RelatedManager

    from apps.catalog.models.curriculum_item import CurriculumItem


class CourseQuerySet(models.QuerySet["Course"]):
    def featured(self) -> Self:
        return self.filter(is_published=True).prefetch_related("curriculum").order_by("id")


class CourseManager(models.Manager["Course"]):
    def get_queryset(self) -> CourseQuerySet:
        return CourseQuerySet(self.model, using=self._db)

    def featured_course(self) -> Course | None:
        return self.get_queryset().featured().first()


class Course(TimeMixinModel):
    title = models.CharField("교육명", max_length=120)
    slug = models.SlugField("슬러그", unique=True)
    summary = models.CharField("한 줄 소개", max_length=200)
    description = models.TextField("설명")
    hero_image = models.ImageField("대표 이미지", upload_to="courses/", blank=True)
    hero_alt = models.CharField("대표 이미지 설명", max_length=200, blank=True)
    is_published = models.BooleanField("공개", default=False)
    curriculum: RelatedManager[CurriculumItem]

    objects = CourseManager()

    class Meta:
        verbose_name = "교육"
        verbose_name_plural = "교육"
        ordering = ("id",)

    def __str__(self):
        return self.title
