from django.contrib import admin

from .models import Author, Book, BookComment


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ["name", "date_of_birth", "bio_short", "preview"]
    fields = ["name", "date_of_birth", "bio", "photo", "preview"]
    readonly_fields = ["preview"]
    search_fields = ["name", "date_of_birth"]


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "author",
        "publication_year",
        "summary_short",
        "preview",
        "added_by",
    ]
    fields = [
        "title",
        "author",
        "summary",
        "publication_year",
        "poster",
        "preview",
        "added_by",
    ]
    readonly_fields = ["preview"]
    search_fields = ["title", "author__name"]


@admin.register(BookComment)
class BookCommentAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "book",
        "content",
        "created_at",
    ]
    fields = ["user", "book", "content", "created_at"]
    readonly_fields = ["created_at"]
