from storybase.views.generic import ModelIdDetailView


class SharePopupView(ModelIdDetailView):
    """
    Base view for popup content for sharing an item

    This view provides the HTML for a popup window of sharing tools.
    It is designed to be fetched via an asynchronous request from
    JavaScript.

    """
    template_name = 'storybase/share_popup.html'


class ShareView(ModelIdDetailView):
    """
    Base view for standalone page for sharing an item

    The template just wraps ``storybase/share_popup.html``
    """
    template_name = 'storybase/share.html'


class EmbedPopupView(ModelIdDetailView):
    """
    Base view for popup content for embeding an item

    While other views provide the HTML for the widget embedded
    in a partner website, this view provides the HTML for a popup window
    of sharing tools.  It is designed to be fetched via an asynchronous
    request from JavaScript

    """
    template_name = 'storybase/embed_popup.html'


class EmbedView(ModelIdDetailView):
    """
    Base view for standalone page for embedding an item

    The template just wraps ``storybase/embed_popup.html``
    """
    template_name = 'storybase/embed.html'
