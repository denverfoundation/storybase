from django.contrib.auth.tokens import default_token_generator
from django.utils.translation import ugettext_lazy as _

def send_password_reset_email(user, domain_override=None, 
                              email_template_name='registration/password_reset_email.html',
                              use_https=False, 
                              token_generator=default_token_generator, 
                              from_email=None, request=None,
                              extra_context={}):
    """
    Send a password reset e-mail

    Based on django.contrib.auth.forms.ResetPasswordForm.save()

    """
    import logging
    from django.core.mail import send_mail
    from django.contrib.sites.models import get_current_site
    from django.template import Context, loader
    from django.utils.http import int_to_base36

    logger = logging.getLogger('storybase_user.admin')

    if not domain_override:
        current_site = get_current_site(request)
        site_name = current_site.name
        domain = current_site.domain
    else:
        site_name = domain = domain_override
    t = loader.get_template(email_template_name)
    c = {
        'email': user.email,
        'domain': domain,
        'site_name': site_name,
        'uid': int_to_base36(user.id),
        'user': user,
        'token': token_generator.make_token(user),
        'protocol': use_https and 'https' or 'http',
    }
    c.update(extra_context)
    send_mail(_("Password reset on %s") % site_name,
        t.render(Context(c)), from_email, [user.email])
    logger.info("Password reset email sent to %s" % (user.email))
