from django.db import models

from apps.common.models import TimeMixinModel


class Course(TimeMixinModel):
    title = models.CharField("교육명", max_length=120)
    slug = models.SlugField("슬러그", unique=True)
    summary = models.CharField("한 줄 소개", max_length=200)
    description = models.TextField("설명")
    hero_image = models.ImageField("대표 이미지", upload_to="courses/", blank=True)
    hero_alt = models.CharField("대표 이미지 설명", max_length=200, blank=True)
    is_published = models.BooleanField("공개", default=False)

    class Meta:
        verbose_name = "교육"
        verbose_name_plural = "교육"
        ordering = ("id",)

    def __str__(self):
        return self.title
