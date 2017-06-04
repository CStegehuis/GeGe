from django.shortcuts import redirect, get_object_or_404, render
from core.models import Publication, AboutPage

from core.models import ArchivePage


def archive(request):
    pages = ArchivePage.objects.all().order_by("-date")
    return render(request, 'archive/archive.html', {
        'pages': pages,
    })