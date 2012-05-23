from decimal import Decimal
import copy
import sys

from django.contrib.gis.utils.layermapping import (InvalidInteger,
    InvalidString, InvalidDecimal, LayerMapping, LayerMapError)
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.gis.gdal import OGRGeometry
from django.contrib.gis.gdal.field import OFTReal, OFTString
from django.db import models, transaction

from storybase.fields import ShortTextField

class ExtraLayerMapping(LayerMapping):
    """
    A custom version of ``LayerMapping``
    
    This class provides a ``save()`` method that allows initializing some
    of the the spatial model attributes that aren't contained in the 
    OGR vector files.

    """
    FIELD_TYPES = copy.copy(LayerMapping.FIELD_TYPES)
    FIELD_TYPES.update({
        ShortTextField : OFTString
    })

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

    def save(self, verbose=False, fid_range=False, step=False,
             progress=False, silent=False, stream=sys.stdout, strict=False,
             model_kwargs=None):
        """
        Saves the contents from the OGR DataSource Layer into the database
        according to the mapping dictionary given at initialization.

        Keyword Parameters:
         verbose:
           If set, information will be printed subsequent to each model save
           executed on the database.

         fid_range:
           May be set with a slice or tuple of (begin, end) feature ID's to map
           from the data source.  In other words, this keyword enables the user
           to selectively import a subset range of features in the geographic
           data source.

         step:
           If set with an integer, transactions will occur at every step
           interval. For example, if step=1000, a commit would occur after
           the 1,000th feature, the 2,000th feature etc.

         progress:
           When this keyword is set, status information will be printed giving
           the number of features processed and sucessfully saved.  By default,
           progress information will pe printed every 1000 features processed,
           however, this default may be overridden by setting this keyword with an
           integer for the desired interval.

         stream:
           Status information will be written to this file handle.  Defaults to
           using `sys.stdout`, but any object with a `write` method is supported.

         silent:
           By default, non-fatal error notifications are printed to stdout, but
           this keyword may be set to disable these notifications.

         strict:
           Execution of the model mapping will cease upon the first error
           encountered.  The default behavior is to attempt to continue.

         model_kwargs:
           Keyword arguments passed to the model constructor.  This allows
           for the initialization of model attributes not found in the
           vector file.
        """
        # Getting the default Feature ID range.
        default_range = self.check_fid_range(fid_range)

        # Setting the progress interval, if requested.
        if progress:
            if progress is True or not isinstance(progress, int):
                progress_interval = 1000
            else:
                progress_interval = progress

        # Defining the 'real' save method, utilizing the transaction
        # decorator created during initialization.
        @self.transaction_decorator
        def _save(feat_range=default_range, num_feat=0, num_saved=0):
            if feat_range:
                layer_iter = self.layer[feat_range]
            else:
                layer_iter = self.layer

            for feat in layer_iter:
                num_feat += 1
                # Getting the keyword arguments
                try:
                    kwargs = self.feature_kwargs(feat)
                except LayerMapError, msg:
                    # Something borked the validation
                    if strict: raise
                    elif not silent:
                        stream.write('Ignoring Feature ID %s because: %s\n' % (feat.fid, msg))
                else:
                    # Constructing the model using the keyword args
                    # Add additional keyword arguments
                    if model_kwargs:
                        kwargs.update(model_kwargs)
                    is_update = False
                    if self.unique:
                        # If we want unique models on a particular field, handle the
                        # geometry appropriately.
                        try:
                            # Getting the keyword arguments and retrieving
                            # the unique model.
                            u_kwargs = self.unique_kwargs(kwargs)
                            m = self.model.objects.using(self.using).get(**u_kwargs)
                            is_update = True

                            # Getting the geometry (in OGR form), creating
                            # one from the kwargs WKT, adding in additional
                            # geometries, and update the attribute with the
                            # just-updated geometry WKT.
                            geom = getattr(m, self.geom_field).ogr
                            new = OGRGeometry(kwargs[self.geom_field])
                            for g in new: geom.add(g)
                            setattr(m, self.geom_field, geom.wkt)
                        except ObjectDoesNotExist:
                            # No unique model exists yet, create.
                            m = self.model(**kwargs)
                    else:
                        m = self.model(**kwargs)

                    try:
                        # Attempting to save.
                        m.save(using=self.using)
                        num_saved += 1
                        if verbose: stream.write('%s: %s\n' % (is_update and 'Updated' or 'Saved', m))
                    except SystemExit:
                        raise
                    except Exception, msg:
                        if self.transaction_mode == 'autocommit':
                            # Rolling back the transaction so that other model saves
                            # will work.
                            transaction.rollback_unless_managed()
                        if strict:
                            # Bailing out if the `strict` keyword is set.
                            if not silent:
                                stream.write('Failed to save the feature (id: %s) into the model with the keyword arguments:\n' % feat.fid)
                                stream.write('%s\n' % kwargs)
                            raise
                        elif not silent:
                            stream.write('Failed to save %s:\n %s\nContinuing\n' % (kwargs, msg))

                # Printing progress information, if requested.
                if progress and num_feat % progress_interval == 0:
                    stream.write('Processed %d features, saved %d ...\n' % (num_feat, num_saved))

            # Only used for status output purposes -- incremental saving uses the
            # values returned here.
            return num_saved, num_feat

        nfeat = self.layer.num_feat
        if step and isinstance(step, int) and step < nfeat:
            # Incremental saving is requested at the given interval (step)
            if default_range:
                raise LayerMapError('The `step` keyword may not be used in conjunction with the `fid_range` keyword.')
            beg, num_feat, num_saved = (0, 0, 0)
            indices = range(step, nfeat, step)
            n_i = len(indices)

            for i, end in enumerate(indices):
                # Constructing the slice to use for this step; the last slice is
                # special (e.g, [100:] instead of [90:100]).
                if i+1 == n_i: step_slice = slice(beg, None)
                else: step_slice = slice(beg, end)

                try:
                    num_feat, num_saved = _save(step_slice, num_feat, num_saved)
                    beg = end
                except:
                    stream.write('%s\nFailed to save slice: %s\n' % ('=-' * 20, step_slice))
                    raise
        else:
            # Otherwise, just calling the previously defined _save() function.
            _save()
