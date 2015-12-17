"""Views used by custom social_auth pipeline"""

from django.conf import settings
from django.core.urlresolvers import reverse
from django.views.generic.edit import FormView

from storybase_user.social_auth.forms import TosForm, EmailTosForm

class GetExtraAccountDetailsView(FormView):
    """Get additional user data during association with OAuth account"""
    template_name = "storybase_user/account_extra_details.html"

    def _get_backend(self):
        """Get which social_auth backend is being used"""
        name = getattr(settings, 'SOCIAL_AUTH_PARTIAL_PIPELINE_KEY',
                       'partial_pipeline')
        return self.request.session[name]['backend']

    def form_valid(self, form):
        self.request.session['new_account_email'] = form.cleaned_data.get('email', None)
        self.request.session['new_account_extra_details'] = True
        return super(GetExtraAccountDetailsView, self).form_valid(form)

    def get_form_class(self):
        backend = self._get_backend()
        if backend == 'twitter':
            return EmailTosForm
        else:
            return TosForm

    def get_success_url(self):
        backend = self._get_backend()
        success_url = reverse('socialauth_complete', kwargs={'backend': backend})
        return success_url
