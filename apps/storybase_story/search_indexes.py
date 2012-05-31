from haystack import indexes

from models import Story

class GeoHashMultiValueField(indexes.MultiValueField):
    field_type = 'geohash'

class StoryIndex(indexes.RealTimeSearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    author = indexes.FacetCharField(model_attr='author')
    published = indexes.FacetDateTimeField(model_attr='published')
    created = indexes.FacetDateTimeField(model_attr='created')
    last_edited = indexes.FacetDateTimeField(model_attr='last_edited')
    # TODO: Use a meta class to dynamically populate these from "official"
    # tag sets 
    topic_ids = indexes.FacetMultiValueField()
    organization_ids = indexes.FacetMultiValueField()
    project_ids = indexes.FacetMultiValueField()
    language_ids = indexes.FacetMultiValueField()
    place_ids = indexes.FacetMultiValueField()
    points = GeoHashMultiValueField()
    num_points = indexes.IntegerField()

    def get_model(self):
        return Story

    def prepare_topic_ids(self, obj):
        return [topic.id for topic in obj.topics.all()]

    def prepare_organization_ids(self, obj):
        return [organization.organization_id for organization in obj.organizations.all()]

    def prepare_project_ids(self, obj):
        return [project.project_id for project in obj.projects.all()]

    def prepare_language_ids(self, obj):
        return obj.get_languages()

    def prepare_place_ids(self, obj):
        return [place.place_id for place in obj.inherited_places]

    def prepare_points(self, obj):
        return ["%s,%s" % (point[0], point[1]) for point in obj.points]

    def prepare_num_points(self, obj):
        return len(obj.points)

    def index_queryset(self):
        return Story.objects.filter(status__exact='published')

    def should_update(self, instance, **kwargs):
        """
        Determine if an object should be updated in the index.
        """
        should_update = True
        translation_set = getattr(instance, instance.translation_set)
        if translation_set.count() == 0:
            should_update = False
        return should_update
