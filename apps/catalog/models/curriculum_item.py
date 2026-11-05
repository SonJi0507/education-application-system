from django.db import models


class CurriculumItem(models.Model):
    course = models.ForeignKey(
        "catalog.Course",
        verbose_name="교육",
        related_name="curriculum",
        on_delete=models.CASCADE,
    )
    position = models.PositiveIntegerField("순서")
    title = models.CharField("제목", max_length=120)
    body = models.TextField("내용")

    class Meta:
        verbose_name = "커리큘럼"
        verbose_name_plural = "커리큘럼"
        ordering = ("position", "id")
        constraints = (
            models.UniqueConstraint(
                fields=["course", "position"],
                name="unique_curriculum_position",
            ),
        )

    def __str__(self):
        return f"{self.position}. {self.title}"
