from decimal import Decimal
import copy

from django.contrib.gis.utils.layermapping import (InvalidInteger,
    InvalidString, InvalidDecimal, LayerMapping as DistLayerMapping)
    
from django.contrib.gis.gdal.field import OFTReal, OFTString
from django.db import models

from storybase.fields import ShortTextField

class LayerMapping(DistLayerMapping):
    """
    A custom version of ``LayerMapping``

    This class knows about my ShortTextField and also has a patch for
    Django bug #18367
    """
    FIELD_TYPES = copy.copy(DistLayerMapping.FIELD_TYPES)
    FIELD_TYPES.update({
        ShortTextField : OFTString
    })

    # TODO: Remove this override if we switch to a version of Django
    # with the fix for #18367 applied
    def verify_ogr_field(self, ogr_field, model_field):
        """
        Verifies if the OGR Field contents are acceptable to the Django
        model field.  If they are, the verified value is returned,
        otherwise the proper exception is raised.
        """
        if (isinstance(ogr_field, OFTString) and
            isinstance(model_field, (models.CharField, models.TextField))):
            if self.encoding:
                # The encoding for OGR data sources may be specified here
                # (e.g., 'cp437' for Census Bureau boundary files).
                val = unicode(ogr_field.value, self.encoding)
            else:
                val = ogr_field.value
                if model_field.max_length and len(val) > model_field.max_length:
                    raise InvalidString('%s model field maximum string length is %s, given %s characters.' %
                                        (model_field.name, model_field.max_length, len(val)))
        elif isinstance(ogr_field, OFTReal) and isinstance(model_field, models.DecimalField):
            try:
                # Creating an instance of the Decimal value to use.
                d = Decimal(str(ogr_field.value))
            except:
                raise InvalidDecimal('Could not construct decimal from: %s' % ogr_field.value)

            # Getting the decimal value as a tuple.
            dtup = d.as_tuple()
            digits = dtup[1]
            d_idx = dtup[2] # index where the decimal is

            # Maximum amount of precision, or digits to the left of the decimal.
            max_prec = model_field.max_digits - model_field.decimal_places

            # Getting the digits to the left of the decimal place for the
            # given decimal.
            if d_idx < 0:
                n_prec = len(digits[:d_idx])
            else:
                n_prec = len(digits) + d_idx

            # If we have more than the maximum digits allowed, then throw an
            # InvalidDecimal exception.
            if n_prec > max_prec:
                raise InvalidDecimal('A DecimalField with max_digits %d, decimal_places %d must round to an absolute value less than 10^%d.' %
                                     (model_field.max_digits, model_field.decimal_places, max_prec))
            val = d
        elif isinstance(ogr_field, (OFTReal, OFTString)) and isinstance(model_field, models.IntegerField):
            # Attempt to convert any OFTReal and OFTString value to an OFTInteger.
            try:
                val = int(ogr_field.value)
            except:
                raise InvalidInteger('Could not construct integer from: %s' % ogr_field.value)
        else:
            val = ogr_field.value
        return val
