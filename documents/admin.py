from django.contrib import admin

from .models import Document, DocumentCategory


@admin.register(DocumentCategory)
class DocumentCategoryAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "is_active",
        "created_at",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "name",
        "description",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "document_type",
        "category",
        "access_level",
        "is_published",
        "download_count",
        "uploaded_by",
        "created_at",
    )

    list_filter = (
        "document_type",
        "category",
        "access_level",
        "is_published",
        "created_at",
    )

    search_fields = (
        "title",
        "description",
        "slug",
        "category__name",
    )

    prepopulated_fields = {
        "slug": ("title",)
    }

    readonly_fields = (
        "download_count",
        "created_at",
        "updated_at",
    )

    autocomplete_fields = (
        "uploaded_by",
    )