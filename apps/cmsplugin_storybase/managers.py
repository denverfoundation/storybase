from django.db import models
from cms.utils.i18n import get_fallback_languages

class TeaserManager(models.Manager):
    def get_teaser(self, page, language, language_fallback=False):
        """
        Gets the latest content for a particular page and language. Falls back
        to another language if wanted.
        """
        try:
            teaser = self.get(language=language, page=page)
            return teaser
        except self.model.DoesNotExist:
            if language_fallback:
                try:
                    teasers = self.filter(page=page)
                    fallbacks = get_fallback_languages(language)
                    for lang in fallbacks:
                        for teaser in teasers:
                            if lang == teaser.language:
                                return teaser
                    return None
                except self.model.DoesNotExist:
                    pass
            else:
                raise
        return None
