from django.conf import settings
from django.http import Http404
from django.shortcuts import redirect, render
from django.utils import translation
from models import get_asset, Asset

def asset_detail(request, **kwargs):
    try:
        language_code = translation.get_language()
        asset = get_asset(asset_id=kwargs['asset_id'])
        available_languages = asset.get_languages()
        if language_code not in available_languages:
            alt_lang = settings.LANGUAGE_CODE
            if alt_lang not in available_languages:
                alt_lang = available_languages[0]
            path = asset.get_absolute_url()
            return redirect('/%s%s' % (alt_lang, path))
    except Asset.DoesNotExist:
        raise Http404
    return render(request, 'storybase_asset/asset_detail.html', 
                  {'asset': asset})
