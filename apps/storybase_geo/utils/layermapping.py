import copy

from django.contrib.gis.utils.layermapping import LayerMapping as DistLayerMapping
from django.contrib.gis.gdal.field import OFTString

from storybase.fields import ShortTextField

class LayerMapping(DistLayerMapping):
    """
    A custom version of ``LayerMapping``

    This class knows about my ShortTextField
    """
    FIELD_TYPES = copy.copy(DistLayerMapping.FIELD_TYPES)
    FIELD_TYPES.update({
        ShortTextField : OFTString
    })
