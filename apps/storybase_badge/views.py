from django.views.generic import TemplateView
from .models import Badge


class BadgesView(TemplateView):
    template_name = 'badges.html'

    def get_context_data(self, **kwargs):
        context = super(BadgesView, self).get_context_data(**kwargs)
        context['badges'] = Badge.objects.all()

        return context
