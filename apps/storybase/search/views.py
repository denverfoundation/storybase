from django.shortcuts import render_to_response
from haystack.views import SearchView

class StorybaseSearchView(SearchView):
    def create_response(self):
        """
        Generates the actual HttpResponse to send back to the user.

        This custom version adds spelling suggestions even if there are no
        results.  For some reason I don't understand, the default
        ``SearchView.create_response`` only returns spelling suggestions
        if there are results of the search.

        """
        (paginator, page) = self.build_page()

        context = {
            'query': self.query,
            'form': self.form,
            'page': page,
            'paginator': paginator,
            'suggestion': None,
        }

        if hasattr(self.results, 'query') and self.results.query.backend.include_spelling:
            context['suggestion'] = self.form.get_suggestion()

        context.update(self.extra_context())
        return render_to_response(self.template, context, context_instance=self.context_class(self.request))
