from wagtail.wagtailcore.models import Page, Orderable
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailadmin.edit_handlers import (FieldPanel,
                                                InlinePanel,
                                                MultiFieldPanel,
                                                StreamFieldPanel,
                                                TabbedInterface,
                                                ObjectList)
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailsearch import index
from core.fields import TagManager
from django.db.models.fields import TextField, CharField
from django.utils import timezone
# from wagtail_embed_videos.edit_handlers import EmbedVideoChooserPanel
from babel.dates import format_date
from wagtail.wagtailsnippets.edit_handlers import SnippetChooserPanel


from wagtail.wagtailsnippets.models import register_snippet

from django import forms
from django.db import models

from modelcluster.fields import ParentalKey, ParentalManyToManyField
from modelcluster.tags import ClusterTaggableManager
from taggit.models import TaggedItemBase

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from core.helpers import paginate


# =================================================================
# Snippets
#=================================================================
@register_snippet
class Publication(models.Model):
    title = models.CharField(null=True, default="", max_length=999)
    subtitle = models.CharField(blank=False, null=False, default="", max_length=999)
    source = CharField(null=False, default="", blank=False, max_length=999)
    url_source = CharField(null=True, default="", blank=True, max_length=999)
    description = TextField(null=False, default="", help_text="Description")
    date = models.DateTimeField("Post date", default=None)

    publication_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    panels = [
        FieldPanel('title'),
        FieldPanel('subtitle'),
        FieldPanel('date'),
        FieldPanel('source'),
        FieldPanel('url_source'),
        FieldPanel('description'),
        ImageChooserPanel('publication_image')
    ]

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Publication"
        ordering = ["title"]

    @property
    def pretty_date(self):
        return format_date(self.date, locale='nl', format="LLL YYYY")


class AboutPagePublication(Orderable, models.Model):
    page = ParentalKey('AboutPage', related_name='publications_about')
    publication = models.ForeignKey('Publication', related_name='+')

    class Meta:
        verbose_name = "publication_about"
        verbose_name_plural = "publications_about"

    panels = [
        SnippetChooserPanel('publication')
    ]

    def __str__(self):
        return self.page.title + self.publication.title

# =================================================================
# Tag page
#=================================================================

class BlogTagIndexPage(Page):

    def get_context(self, request):

        # Filter by tag
        tag = request.GET.get('tag')
        blogpages = BlogPage.objects.filter(tags__name=tag)

        # Update template context
        context = super(BlogTagIndexPage, self).get_context(request)
        context['blogpages'] = blogpages
        return context


class BlogPageTag(TaggedItemBase):
    content_object = ParentalKey('BlogPage', related_name='tagged_items')

    def __str__(self):
        return self.tag.slug


# =================================================================
# Blog page
#=================================================================
class BlogPage(Page):
    date = models.DateField("Post date", default=timezone.now)
    intro = models.CharField(max_length=250, default="")
    # body = RichTextField(blank=True)
    source = models.CharField(max_length=250, blank=True, default="")
    publish_date = models.DateField("Published date", blank=True)
    text = RichTextField(blank=True, default="")
    tags = ClusterTaggableManager(through=BlogPageTag, blank=True)
    # tags = TagManager(through=BlogPageTag, blank=True)

    categories = ParentalManyToManyField('BlogCategory', blank=True)
    reeks = ParentalManyToManyField('BlogReeks', blank=True)

    def main_image(self):
        gallery_item = self.gallery_images.first()
        if gallery_item:
            return gallery_item.image
        else:
            return None

    search_fields = Page.search_fields + [
        index.SearchField('title', boost=4, partial_match=True),
        index.SearchField('intro'),
        # index.SearchField('body'),
        index.SearchField('source'),
        index.SearchField('tag_id'),
        index.SearchField('tag_name'),
        index.SearchField('categories'),
    ]

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('date'),
            FieldPanel('tags'),
            FieldPanel('source'),
            FieldPanel('publish_date'),
            FieldPanel('text'),
            FieldPanel('reeks', widget=forms.CheckboxSelectMultiple),
            FieldPanel('categories', widget=forms.CheckboxSelectMultiple),
        ], heading="Blog information"),
        FieldPanel('intro'),
        # FieldPanel('body'),
        InlinePanel('gallery_images', label="Gallery images"),
    ]

    class Meta:
        verbose_name = "Blog"
        ordering = ["-date"]

    @property
    def tag_id(self):
        tags = list(self.tags.all())
        return [tag.id for tag in tags]

    @property
    def tag_name(self):
        tags = list(self.tags.all())
        return [tag.slug for tag in tags]


class BlogPageGalleryImage(Orderable):
    page = ParentalKey(BlogPage, related_name='gallery_images')
    image = models.ForeignKey(
        'wagtailimages.Image', on_delete=models.CASCADE, related_name='+'
    )
    caption = models.CharField(blank=True, max_length=250)

    panels = [
        ImageChooserPanel('image'),
        FieldPanel('caption'),
    ]


# =================================================================
# Blog Index page
#=================================================================

class BlogIndexPage(Page):
    intro = RichTextField(blank=True)

    def get_context(self, request):
        # Update context to include only published posts, ordered by reverse-chron
        context = super(BlogIndexPage, self).get_context(request)
        # page = request.GET.get('page')
        blogpages = self.get_children().live().order_by('-first_published_at')
        context['blogpages'] = blogpages
        # paginator = Paginator(blogpages, 4)
        #
        # return {'blogs': paginate(paginator, context['request'].GET.get('page'))}
        # try:
        #     context['blogs'] = paginator.page(page)
        # except PageNotAnInteger:
        #     # If page is not an integer, deliver first page.
        #     context['blogs'] = paginator.page(1)
        # except EmptyPage:
        #     # If page is out of range (e.g. 9999), deliver last page of results.
        #     context['blogs'] = paginator.page(paginator.num_pages)

        return context


# =================================================================
# Category page
#=================================================================

@register_snippet
class BlogCategory(models.Model):
    name = CharField(max_length=255)
    icon = models.ForeignKey(
        'wagtailimages.Image', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='+'
    )

    panels = [
        FieldPanel('name'),
        ImageChooserPanel('icon'),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'blog categories'


class BlogPageCategory(TaggedItemBase):
    content_object = ParentalKey('BlogPage', related_name='categorized_items')

    def __str__(self):
        return self.category.slug

class BlogCategoryIndexPage(Page):
    intro = RichTextField(blank=True)

    def get_context(self, request):

        # Filter by tag
        category = request.GET.get('category')
        blogpages = BlogPage.objects.filter(categories__name=category)

        # Update template context
        context = super(BlogCategoryIndexPage, self).get_context(request)
        context['blogpages'] = blogpages
        return context

# =================================================================
# About page
#=================================================================
class AboutPage(Page):
    body = RichTextField(blank=True)

    def main_image(self):
        gallery_item = self.gallery_images.first()
        if gallery_item:
            return gallery_item.image
        else:
            return None

    content_panels = Page.content_panels + [
        FieldPanel('body', classname="full"),
        InlinePanel('gallery_images', label="Gallery images"),

    ]

    meta_panels = [
        InlinePanel('publications_about', label="Publication(s)"),
    ]

    edit_handler = TabbedInterface([
        ObjectList(content_panels, heading='Content'),
        ObjectList(meta_panels, heading='Meta'),
        ObjectList(Page.promote_panels, heading='Promote'),
        ObjectList(
            Page.settings_panels,
            heading='Settings',
            classname="settings"
        ),
    ])


class AboutPageGalleryImage(Orderable):
    page = ParentalKey(AboutPage, related_name='gallery_images')
    image = models.ForeignKey(
        'wagtailimages.Image', on_delete=models.CASCADE, related_name='+'
    )
    caption = models.CharField(blank=True, max_length=250)

    panels = [
        ImageChooserPanel('image'),
        FieldPanel('caption'),
    ]



# =================================================================
# Media page
#=================================================================
class MediaPage(Page):
    body = RichTextField(blank=True)
    subtitle = CharField(null=True, default="", blank=True, max_length=999)
    # teaser = TextField(null=True, default="", blank=True, help_text="Will be \
    #     used in media index page")
    intro = TextField(null=False, default="", help_text="Introduction")
    date = models.DateTimeField("Post date", default=timezone.now)
    source = CharField(null=False, default="", blank=False, max_length=999)
    url_source = CharField(null=True, default="", blank=True, max_length=999)

    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    image_as_cover = models.BooleanField(
        verbose_name='Use image as cover',
        default=False,
        help_text='To be used as a cover the image should be at least \
            910 pixels wide'
    )


    content_panels = [
        MultiFieldPanel(
            (
                ImageChooserPanel('image'),
                FieldPanel('image_as_cover'),
            ),
            'Image'
        )
    ] + Page.content_panels + [
        FieldPanel('subtitle'),
        FieldPanel('intro'),
        FieldPanel('body'),
        FieldPanel('date'),
        FieldPanel('source'),
        FieldPanel('url_source'),
    ]

    # content_panels = Page.content_panels + [
    #     FieldPanel('subtitle'),
    #     FieldPanel('body'),
    #     FieldPanel('intro'),
    #     FieldPanel('date'),
    # ]


class MediaIndexPage(Page):
    intro = RichTextField(blank=True)

    def get_context(self, request):
        # Update context to include only published posts, ordered by reverse-chron
        context = super(MediaIndexPage, self).get_context(request)

        mediapages = self.get_children().live().order_by('-first_published_at')
        context['mediapages'] = mediapages

        return context



# =================================================================
# Archive page
#=================================================================
class ArchivePage(Page):
    body = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('body', classname="full"),
    ]

    @property
    def year_date(self):
        return format_date(self.date, locale='nl', format="YYYY")

    def get_context(self, request):
        # Update context to include only published posts, ordered by reverse-chron
        context = super(ArchivePage, self).get_context(request)
        archivepages = BlogPage.objects.all().live().order_by('-date')
        context['archivepages'] = archivepages

        return context


# =================================================================
# Reeks page
#=================================================================

@register_snippet
class BlogReeks(models.Model):
    name = models.CharField(max_length=255)

    panels = [
        FieldPanel('name'),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'blog reeksen'


class BlogReeksIndexPage(Page):
    intro = RichTextField(blank=True)

    def get_context(self, request):

        # Filter by tag
        reeks = request.GET.get('reeks')
        blogpages = BlogPage.objects.filter(reeks__name=reeks)

        # Update template context
        context = super(BlogReeksIndexPage, self).get_context(request)
        context['blogpages'] = blogpages
        return context