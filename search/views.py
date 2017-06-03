from __future__ import absolute_import, unicode_literals

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import render

from wagtail.wagtailcore.models import Page
from wagtail.wagtailsearch.models import Query

from core.models import BlogPage
from .forms import SearchForm


def search(request):
    search_query = request.GET.get('query', None)
    page = request.GET.get('page', 1)

    search_on = BlogPage.objects.live()

    # Search
    if search_query:
        search_results = search_on.search(search_query)
        query = Query.get(search_query)

        # Record hit
        query.add_hit()
    else:
        search_results = BlogPage.objects.none()

    # Pagination
    paginator = Paginator(search_results, 10)
    try:
        search_results = paginator.page(page)
    except PageNotAnInteger:
        search_results = paginator.page(1)
    except EmptyPage:
        search_results = paginator.page(paginator.num_pages)

    # form = None
    # if request.method == 'GET':
    #     form = SearchForm(request.GET)
    #     for agg, values in aggs.items():
    #         choices = [(key, "%s (%d)" % (key, value)) for key, value in values.items()]
    #         form.fields[agg].choices = choices

    return render(request, 'search/search.html', {
        'search_query': search_query,
        'search_results': search_results,
    })
