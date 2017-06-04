from __future__ import unicode_literals
from core.models import *
from django.db import models

from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailadmin.edit_handlers import FieldPanel


class HomePage(Page):
    body = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('body', classname="full"),
    ]

    def get_context(self, request):

        # Update template context
        context = super(HomePage, self).get_context(request)
        blogpages = BlogPage.objects.all().live()

        context['blogpages'] = blogpages
        return context