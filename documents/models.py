from django.conf import settings
from django.db import models


class DocumentCategory(models.Model):

    name = models.CharField(
        max_length=150,
        unique=True
    )

    description = models.TextField(
        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Document Category"
        verbose_name_plural = "Document Categories"

    def __str__(self):
        return self.name


class Document(models.Model):

    class AccessLevel(models.TextChoices):

        PUBLIC = "PUBLIC", "Public"

        MEMBERS = "MEMBERS", "Members Only"

        STAFF = "STAFF", "Staff Only"

        ADMIN = "ADMIN", "Administrators Only"


    class DocumentType(models.TextChoices):

        CONSTITUTION = "CONSTITUTION", "Constitution"

        BYLAWS = "BYLAWS", "Bylaws"

        MINUTES = "MINUTES", "Meeting Minutes"

        FINANCIAL = "FINANCIAL", "Financial Statement"

        AGM = "AGM", "AGM Document"

        CIRCULAR = "CIRCULAR", "Circular"

        POLICY = "POLICY", "Policy"

        CERTIFICATE = "CERTIFICATE", "Certificate"

        MEMBERSHIP = "MEMBERSHIP", "Membership Document"

        ADMINISTRATIVE = "ADMINISTRATIVE", "Administrative"

        OTHER = "OTHER", "Other"


    title = models.CharField(
        max_length=250
    )

    slug = models.SlugField(
        max_length=280,
        unique=True
    )

    category = models.ForeignKey(
        DocumentCategory,
        on_delete=models.PROTECT,
        related_name="documents"
    )

    document_type = models.CharField(
        max_length=30,
        choices=DocumentType.choices,
        default=DocumentType.OTHER
    )

    description = models.TextField(
        blank=True
    )

    file = models.FileField(
        upload_to="documents/%Y/%m/"
    )

    access_level = models.CharField(
        max_length=20,
        choices=AccessLevel.choices,
        default=AccessLevel.PUBLIC
    )

    is_published = models.BooleanField(
        default=True
    )

    published_at = models.DateTimeField(
        blank=True,
        null=True
    )

    download_count = models.PositiveIntegerField(
        default=0
    )

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="uploaded_documents"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )


    class Meta:
        ordering = [
            "-published_at",
            "-created_at"
        ]

        verbose_name = "Document"
        verbose_name_plural = "Documents"


    def __str__(self):
        return self.title