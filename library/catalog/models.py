import uuid
from datetime import datetime

from accounts.models import User
from django.contrib.postgres.indexes import GinIndex
from django.db import models
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.timezone import now


class UpperGinIndex(GinIndex):
    def create_sql(self, model, schema_editor, using="", *args, **kwargs):
        statement = super().create_sql(
            model, schema_editor, using=using, *args, **kwargs
        )
        quote_name = statement.parts["columns"].quote_name

        def upper_quoted(column):
            return f"UPPER({quote_name(column)})"

        statement.parts["columns"].quote_name = upper_quoted
        return statement


class Author(models.Model):
    id = models.UUIDField(
        verbose_name="ID", primary_key=True, default=uuid.uuid4
    )
    name = models.CharField(
        verbose_name="Имя", max_length=200, blank=False, null=False
    )
    date_of_birth = models.DateField(
        verbose_name="Дата рождения",
        blank=False,
        null=False,
        default=now,
    )
    bio = models.TextField(
        verbose_name="Краткая биография",
        max_length=1000,
        blank=False,
        null=False,
    )
    photo = models.ImageField(
        verbose_name="Фотография",
        upload_to="authors/",
        blank=False,
        null=False,
        default="authors/no-photo.webp",
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Автор"
        verbose_name_plural = "Авторы"
        indexes = [
            UpperGinIndex(
                fields=["name"],
                name="author_name_upper_gin_idx",
                opclasses=["gin_trgm_ops"],
            ),
        ]

    def get_absolute_url(self) -> str:
        return reverse("author-detail", args=[str(self.id)])

    def __str__(self) -> str:
        return self.name

    def bio_short(self):
        return f"{self.bio[:100]}..."

    bio_short.short_description = "Краткая биография"

    def preview(self):
        return mark_safe(
            f"<img src='{self.photo.url}' style='max-height: 200px;'>"
        )

    preview.short_description = "Предпросмотр"


class Book(models.Model):
    id = models.UUIDField(
        verbose_name="ID", primary_key=True, default=uuid.uuid4
    )
    title = models.CharField(
        verbose_name="Название", max_length=200, blank=False, null=False
    )
    author = models.ForeignKey(
        Author,
        verbose_name="Автор",
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        related_name="books",
    )
    summary = models.TextField(
        verbose_name="Краткое описание",
        max_length=1000,
        blank=False,
        null=False,
    )
    publication_year = models.PositiveSmallIntegerField(
        verbose_name="Год издания",
        blank=False,
        null=False,
        default=datetime.now().year,
    )
    poster = models.ImageField(
        verbose_name="Обложка",
        upload_to="posters/",
        blank=False,
        null=False,
        default="posters/no-poster.jpg",
    )
    added_by = models.ForeignKey(
        User,
        verbose_name="Добавил",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ["title", "author__name"]
        verbose_name = "Книга"
        verbose_name_plural = "Книги"
        constraints = [
            models.CheckConstraint(
                check=models.Q(
                    publication_year__gte=0, publication_year__lte=2999
                ),
                name="publication_year_gte_0_lte_2999",
                violation_error_message="Год публикации должен быть в интервале от 0 до 2999",
            ),
        ]
        indexes = [
            UpperGinIndex(
                fields=["title"],
                name="book_title_upper_gin_idx",
                opclasses=["gin_trgm_ops"],
            ),
        ]

    def get_absolute_url(self) -> str:
        return reverse("book-detail", args=[str(self.id)])

    def __str__(self) -> str:
        return f"{self.title}"

    def summary_short(self):
        return f"{self.summary[:100]}..."

    summary_short.short_description = "Краткое описание"

    def preview(self):
        return mark_safe(
            f"<img src='{self.poster.url}' style='max-height: 200px;'>"
        )

    preview.short_description = "Предпросмотр"


class BookComment(models.Model):
    id = models.UUIDField(
        verbose_name="ID", primary_key=True, default=uuid.uuid4
    )
    user = models.ForeignKey(
        User,
        verbose_name="Пользователь",
        on_delete=models.CASCADE,
        blank=False,
        null=False,
    )
    book = models.ForeignKey(
        Book,
        verbose_name="Книга",
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        related_name="comments",
    )
    content = models.TextField(
        verbose_name="Содержание", max_length=1000, blank=False, null=False
    )
    created_at = models.DateTimeField(
        verbose_name="Дата публикации",
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"

    def __str__(self) -> str:
        return f"Комментарий {self.user.username} на книгу {self.book.title}"
