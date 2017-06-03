from django.core.paginator import EmptyPage, PageNotAnInteger
from django.http import Http404


def paginate(paginator, page):
    try:
        return paginator.page(page)
    except PageNotAnInteger:
        return paginator.page(1)
    except EmptyPage:
        raise Http404("")