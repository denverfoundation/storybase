"""Views for the actions app"""

from django.views.generic import CreateView

from storybase_action.forms import SiteContactMessageForm
from storybase_action.models import SiteContactMessage 

class SiteContactMessageCreateView(CreateView):
    model = SiteContactMessage

    def get_form_class(self):
        return SiteContactMessageForm

    def get_success_url(self):
        """
        Determine the URL to redirect to when the form is successfully 
        validated
        """
        # Just redirect to the front page for now
        return "/" 
    
