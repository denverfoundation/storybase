from django.contrib import messages
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.views.generic import CreateView

from storybase_messaging.forms import SiteContactMessageForm
from storybase_messaging.models import SiteContactMessage 

class SiteContactMessageCreateView(CreateView):
    """View for site-wide contact form"""
    model = SiteContactMessage

    def get_form_class(self):
        return SiteContactMessageForm

    def get_success_url(self):
        """
        Determine the URL to redirect to when the form is successfully 
        validated
        """
        success_url = self.request.GET.get('success', None)
        # See if a success URL was passed as part of the querystring
        if success_url:
            return success_url
        else:
            # Just redirect back to the contact page for now
            return reverse('contact')
   
    def form_valid(self, form):
        """
        Save the form instance, set the current object for the view and 
        redirect to get_success_url()

        Flashes a success message to the user
        """
        messages.add_message(self.request, messages.SUCCESS, 
                         _("Thanks! Your message has been submitted to the "
                   "site administrators"),
                 fail_silently=False)

        return super(SiteContactMessageCreateView, self).form_valid(form)

    def form_invalid(self, form):
        messages.add_message(self.request, messages.ERROR,
                 _("Please fill out all required information"),
                 fail_silently=False)
        return super(SiteContactMessageCreateView, self).form_invalid(form)
