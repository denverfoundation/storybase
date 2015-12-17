from django.contrib import messages
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.views.generic import CreateView, DetailView

from storybase_messaging.forms import SiteContactMessageForm
from storybase_messaging.models import SiteContactMessage, StoryNotification

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


class StoryNotificationDetailView(DetailView):
    """View for viewing story notification messages in the browser"""
    queryset = StoryNotification.objects.all()

    def get_context_data(self, **kwargs):
        context = self.object.get_context()
        # Include some additional context since we're showing this in aweb
        # page instead of an email
        context.update({
            'include_page_markup': True,
            'subject': self.object.get_subject(),
        })
        return context

    def render_to_response(self, context, **response_kwargs):
        """
        Returns a response with a template rendered with the given context.
        """
        return self.response_class(
            request = self.request,
            template = self.object.get_body_template(content_type="html"),
            context = context,
            **response_kwargs
        )
