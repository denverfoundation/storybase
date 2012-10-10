from django import template

from storybase_user.utils  import format_user_name as fmt_user_name

register = template.Library()

@register.simple_tag
def format_user_name(user):
    return fmt_user_name(user)

