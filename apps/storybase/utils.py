from django.template.defaultfilters import slugify as django_slugify

def slugify(s):
    slug = django_slugify(s)
    slug = slug[:50]
    return slug.rstrip('-')
