from django import template

register = template.Library()

@register.inclusion_tag("storybase_asset/dataset_list.html")
def dataset_list(datasets, classname=""):
    return {
        'datasets': datasets,
        'classname': classname,
    }
