from django.db.models.signals import post_syncdb
from django.conf import settings
from django.utils.translation import ugettext_noop as _

if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None

if notification:
    def create_notice_types(app, created_models, verbosity, **kwargs):
        notification.create_notice_type("system_message", _("System Message"),
            _("Important information about %s") % settings.STORYBASE_SITE_NAME)

    post_syncdb.connect(create_notice_types, sender=notification)


