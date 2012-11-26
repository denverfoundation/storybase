from haystack.backends.solr_backend import SolrSearchBackend, SolrEngine

class Solr2155SearchBackend(SolrSearchBackend):
    """Custom Search backend with support for multi-value geohash fields

    See https://github.com/dsmiley/SOLR-2155

    To use this, one should also create a custom Solr schema template
    (``search_configuration/solr.xml``) that sets that class of the 
    ``geohash`` fieldtype to ``solr2155.solr.schema.GeoHashField`` instead
    of ``solr.GeoHashField``.

    """
    def build_schema(self, fields):
        def _find_geohash_fields(fields):
            geohash_fields = []
            for field_name, field_class in fields.items():
                if field_class.field_type == "geohash":
                    geohash_fields.append(field_class.index_fieldname)
            return geohash_fields

        def _find_textspell_fields(fields):
            textspell_fields = []
            for field_name, field_class in fields.items():
                if field_class.field_type == "textSpell":
                    textspell_fields.append(field_class.index_fieldname)
            return textspell_fields

        (content_field_name, schema_fields) = super(Solr2155SearchBackend, self).build_schema(fields)
        # HACK: Do a second pass through the fields to properly set
        # the type for geohash and textSpell fields.  
        # This is a little clunky, but better
        # than copying and pasting the implementation from SolrSearchBackend
        # here.
        geohash_fields = _find_geohash_fields(fields)
        textspell_fields = _find_textspell_fields(fields)
        if geohash_fields or textspell_fields:
            new_schema_fields = []
            for field_data in schema_fields:
                if field_data['field_name'] in geohash_fields:
                    field_data['type'] = 'geohash'
                if field_data['field_name'] in textspell_fields:
                    field_data['type'] = 'textSpell'
                new_schema_fields.append(field_data)

            schema_fields = new_schema_fields

        return (content_field_name, schema_fields)

class Solr2155Engine(SolrEngine):
    backend = Solr2155SearchBackend
