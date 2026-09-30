from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import F, Q
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render

from .models import Document, DocumentCategory


def document_list(request):

    documents = Document.objects.filter(
        is_published=True
    ).select_related(
        "category",
        "uploaded_by"
    )

    categories = DocumentCategory.objects.filter(
        is_active=True
    ).order_by("name")

    search_query = request.GET.get(
        "q",
        ""
    ).strip()

    category_id = request.GET.get(
        "category",
        ""
    )

    document_type = request.GET.get(
        "type",
        ""
    )


    if search_query:

        documents = documents.filter(
            Q(title__icontains=search_query)
            |
            Q(description__icontains=search_query)
            |
            Q(category__name__icontains=search_query)
        )


    if category_id:

        documents = documents.filter(
            category_id=category_id
        )


    if document_type:

        documents = documents.filter(
            document_type=document_type
        )


    # Public documents are visible to everyone.
    # Members-only documents require login.

    if request.user.is_authenticated:

        if not (
            request.user.is_superuser
            or request.user.is_staff
        ):

            documents = documents.filter(
                Q(access_level=Document.AccessLevel.PUBLIC)
                |
                Q(access_level=Document.AccessLevel.MEMBERS)
            )

    else:

        documents = documents.filter(
            access_level=Document.AccessLevel.PUBLIC
        )


    context = {
        "documents": documents,
        "categories": categories,
        "document_types": Document.DocumentType.choices,
        "search_query": search_query,
        "selected_category": category_id,
        "selected_type": document_type,
    }


    return render(
        request,
        "documents/document_list.html",
        context
    )


def document_detail(request, slug):

    document = get_object_or_404(
        Document,
        slug=slug,
        is_published=True
    )


    if document.access_level == Document.AccessLevel.MEMBERS:

        if not request.user.is_authenticated:

            messages.warning(
                request,
                "Please login to access this document."
            )

            return redirect(
                "accounts:login"
            )


    elif document.access_level == Document.AccessLevel.STAFF:

        if not (
            request.user.is_authenticated
            and (
                request.user.is_staff
                or request.user.is_superuser
            )
        ):

            raise Http404


    elif document.access_level == Document.AccessLevel.ADMIN:

        if not (
            request.user.is_authenticated
            and request.user.is_superuser
        ):

            raise Http404


    return render(
        request,
        "documents/document_detail.html",
        {
            "document": document
        }
    )


def document_download(request, slug):

    document = get_object_or_404(
        Document,
        slug=slug,
        is_published=True
    )


    # PUBLIC
    if document.access_level == Document.AccessLevel.PUBLIC:
        pass


    # MEMBERS
    elif document.access_level == Document.AccessLevel.MEMBERS:

        if not request.user.is_authenticated:

            messages.warning(
                request,
                "Please login to download this document."
            )

            return redirect(
                "accounts:login"
            )


    # STAFF
    elif document.access_level == Document.AccessLevel.STAFF:

        if not (
            request.user.is_authenticated
            and (
                request.user.is_staff
                or request.user.is_superuser
            )
        ):

            raise Http404


    # ADMIN
    elif document.access_level == Document.AccessLevel.ADMIN:

        if not (
            request.user.is_authenticated
            and request.user.is_superuser
        ):

            raise Http404


    if not document.file:

        raise Http404


    Document.objects.filter(
        pk=document.pk
    ).update(
        download_count=F("download_count") + 1
    )


    response = FileResponse(
        document.file.open("rb"),
        as_attachment=True,
        filename=document.file.name.split("/")[-1]
    )

    return response