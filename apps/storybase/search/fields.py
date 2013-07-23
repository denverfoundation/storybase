from haystack import indexes

class GeoHashMultiValueField(indexes.MultiValueField):
    field_type = 'geohash'

class TextSpellField(indexes.CharField):
    field_type = 'textSpell'
