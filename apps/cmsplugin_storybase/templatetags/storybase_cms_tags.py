"""Template tags to display customizations to Django CMS"""
from django import template
from cms.templatetags.cms_tags import PageAttribute

register = template.Library()

# Patch the {% page_attribute %} tag to allow it to display the teaser
PageAttribute.valid_attributes = PageAttribute.valid_attributes + ["teaser",]
