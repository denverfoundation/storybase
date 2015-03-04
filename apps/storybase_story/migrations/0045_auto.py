# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding M2M table for field badges on 'Story'
        m2m_table_name = db.shorten_name(u'storybase_story_story_badges')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('story', models.ForeignKey(orm[u'storybase_story.story'], null=False)),
            ('badge', models.ForeignKey(orm[u'storybase_badge.badge'], null=False))
        ))
        db.create_unique(m2m_table_name, ['story_id', 'badge_id'])


    def backwards(self, orm):
        # Removing M2M table for field badges on 'Story'
        db.delete_table(db.shorten_name(u'storybase_story_story_badges'))


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'storybase_asset.asset': {
            'Meta': {'object_name': 'Asset'},
            'asset_created': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'asset_id': ('uuidfield.fields.UUIDField', [], {'db_index': 'True', 'unique': 'True', 'max_length': '32', 'blank': 'True'}),
            'attribution': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'datasets': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'assets'", 'blank': 'True', 'to': u"orm['storybase_asset.DataSet']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_edited': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'license': ('django.db.models.fields.CharField', [], {'max_length': '25', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'assets'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'published': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'section_specific': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'source_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "u'draft'", 'max_length': '10'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        u'storybase_asset.dataset': {
            'Meta': {'object_name': 'DataSet'},
            'attribution': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'dataset_created': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'dataset_id': ('uuidfield.fields.UUIDField', [], {'db_index': 'True', 'unique': 'True', 'max_length': '32', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_edited': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'links_to_file': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'datasets'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'published': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'source': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "u'draft'", 'max_length': '10'})
        },
        u'storybase_badge.badge': {
            'Meta': {'object_name': 'Badge'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'icon_uri': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'storybase_geo.geolevel': {
            'Meta': {'object_name': 'GeoLevel'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': u"orm['storybase_geo.GeoLevel']"}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        u'storybase_geo.location': {
            'Meta': {'object_name': 'Location'},
            'address': ('storybase.fields.ShortTextField', [], {'blank': 'True'}),
            'address2': ('storybase.fields.ShortTextField', [], {'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lat': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'lng': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'location_id': ('uuidfield.fields.UUIDField', [], {'db_index': 'True', 'unique': 'True', 'max_length': '32', 'blank': 'True'}),
            'name': ('storybase.fields.ShortTextField', [], {'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'locations'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'point': ('django.contrib.gis.db.models.fields.PointField', [], {'null': 'True', 'blank': 'True'}),
            'postcode': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'raw': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        u'storybase_geo.place': {
            'Meta': {'object_name': 'Place'},
            'boundary': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {'null': 'True', 'blank': 'True'}),
            'children': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'_parents'", 'to': u"orm['storybase_geo.Place']", 'through': u"orm['storybase_geo.PlaceRelation']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'geolevel': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'places'", 'null': 'True', 'to': u"orm['storybase_geo.GeoLevel']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('storybase.fields.ShortTextField', [], {}),
            'place_id': ('uuidfield.fields.UUIDField', [], {'db_index': 'True', 'unique': 'True', 'max_length': '32', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'blank': 'True'})
        },
        u'storybase_geo.placerelation': {
            'Meta': {'unique_together': "(('parent', 'child'),)", 'object_name': 'PlaceRelation'},
            'child': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'place_parent'", 'to': u"orm['storybase_geo.Place']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'place_child'", 'to': u"orm['storybase_geo.Place']"})
        },
        u'storybase_help.help': {
            'Meta': {'object_name': 'Help'},
            'help_id': ('uuidfield.fields.UUIDField', [], {'unique': 'True', 'max_length': '32', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'searchable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'blank': 'True'})
        },
        u'storybase_story.container': {
            'Meta': {'object_name': 'Container'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'})
        },
        u'storybase_story.containertemplate': {
            'Meta': {'object_name': 'ContainerTemplate'},
            'asset_type': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'can_change_asset_type': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'container': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['storybase_story.Container']"}),
            'container_template_id': ('uuidfield.fields.UUIDField', [], {'db_index': 'True', 'unique': 'True', 'max_length': '32', 'blank': 'True'}),
            'help': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['storybase_help.Help']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'section': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['storybase_story.Section']"}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['storybase_story.StoryTemplate']"})
        },
        u'storybase_story.section': {
            'Meta': {'object_name': 'Section'},
            'assets': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'sections'", 'blank': 'True', 'through': u"orm['storybase_story.SectionAsset']", 'to': u"orm['storybase_asset.Asset']"}),
            'children': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'_parents'", 'to': u"orm['storybase_story.Section']", 'through': u"orm['storybase_story.SectionRelation']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'help': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['storybase_help.Help']", 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'layout': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['storybase_story.SectionLayout']", 'null': 'True'}),
            'root': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'section_id': ('uuidfield.fields.UUIDField', [], {'db_index': 'True', 'unique': 'True', 'max_length': '32', 'blank': 'True'}),
            'story': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sections'", 'to': u"orm['storybase_story.Story']"}),
            'template_section': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'template_for'", 'null': 'True', 'to': u"orm['storybase_story.Section']"}),
            'weight': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'storybase_story.sectionasset': {
            'Meta': {'unique_together': "(('section', 'container', 'weight'),)", 'object_name': 'SectionAsset'},
            'asset': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['storybase_asset.Asset']"}),
            'container': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['storybase_story.Container']", 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'section': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['storybase_story.Section']"}),
            'weight': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'storybase_story.sectionlayout': {
            'Meta': {'object_name': 'SectionLayout'},
            'containers': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'layouts'", 'blank': 'True', 'to': u"orm['storybase_story.Container']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'layout_id': ('uuidfield.fields.UUIDField', [], {'db_index': 'True', 'unique': 'True', 'max_length': '32', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            'template': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'storybase_story.sectionlayouttranslation': {
            'Meta': {'object_name': 'SectionLayoutTranslation'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'default': "'en'", 'max_length': '15'}),
            'layout': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['storybase_story.SectionLayout']"}),
            'name': ('storybase.fields.ShortTextField', [], {}),
            'translation_id': ('uuidfield.fields.UUIDField', [], {'unique': 'True', 'max_length': '32', 'blank': 'True'})
        },
        u'storybase_story.sectionrelation': {
            'Meta': {'object_name': 'SectionRelation'},
            'child': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'section_parent'", 'to': u"orm['storybase_story.Section']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'section_child'", 'to': u"orm['storybase_story.Section']"}),
            'weight': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'storybase_story.sectiontranslation': {
            'Meta': {'unique_together': "(('section', 'language'),)", 'object_name': 'SectionTranslation'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'default': "'en'", 'max_length': '15'}),
            'section': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['storybase_story.Section']"}),
            'title': ('storybase.fields.ShortTextField', [], {}),
            'translation_id': ('uuidfield.fields.UUIDField', [], {'unique': 'True', 'max_length': '32', 'blank': 'True'})
        },
        u'storybase_story.story': {
            'Meta': {'object_name': 'Story'},
            'allow_connected': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'assets': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'stories'", 'blank': 'True', 'to': u"orm['storybase_asset.Asset']"}),
            'author': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'stories'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'badges': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'stories'", 'symmetrical': 'False', 'to': u"orm['storybase_badge.Badge']"}),
            'byline': ('django.db.models.fields.TextField', [], {}),
            'contact_info': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'datasets': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'stories'", 'blank': 'True', 'to': u"orm['storybase_asset.DataSet']"}),
            'featured_assets': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'featured_in_stories'", 'blank': 'True', 'to': u"orm['storybase_asset.Asset']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_template': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_edited': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'license': ('django.db.models.fields.CharField', [], {'max_length': '25', 'blank': 'True'}),
            'locations': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'stories'", 'blank': 'True', 'to': u"orm['storybase_geo.Location']"}),
            'on_homepage': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'organizations': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'stories'", 'blank': 'True', 'to': u"orm['storybase_user.Organization']"}),
            'places': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'stories'", 'blank': 'True', 'to': u"orm['storybase_geo.Place']"}),
            'projects': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'stories'", 'blank': 'True', 'to': u"orm['storybase_user.Project']"}),
            'published': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'related_stories': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'related_to'", 'blank': 'True', 'through': u"orm['storybase_story.StoryRelation']", 'to': u"orm['storybase_story.Story']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "u'draft'", 'max_length': '10'}),
            'story_id': ('uuidfield.fields.UUIDField', [], {'db_index': 'True', 'unique': 'True', 'max_length': '32', 'blank': 'True'}),
            'structure_type': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'template_story': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'template_for'", 'null': 'True', 'to': u"orm['storybase_story.Story']"}),
            'topics': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'stories'", 'blank': 'True', 'to': u"orm['storybase_taxonomy.Category']"}),
            'weight': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'storybase_story.storyrelation': {
            'Meta': {'object_name': 'StoryRelation'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'relation_id': ('uuidfield.fields.UUIDField', [], {'unique': 'True', 'max_length': '32', 'blank': 'True'}),
            'relation_type': ('django.db.models.fields.CharField', [], {'default': "'connected'", 'max_length': '25'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'target'", 'to': u"orm['storybase_story.Story']"}),
            'target': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'source'", 'to': u"orm['storybase_story.Story']"})
        },
        u'storybase_story.storytemplate': {
            'Meta': {'object_name': 'StoryTemplate'},
            'examples': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'example_for'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['storybase_story.Story']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.CharField', [], {'max_length': '140', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            'story': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['storybase_story.Story']", 'null': 'True', 'blank': 'True'}),
            'template_id': ('uuidfield.fields.UUIDField', [], {'db_index': 'True', 'unique': 'True', 'max_length': '32', 'blank': 'True'}),
            'time_needed': ('django.db.models.fields.CharField', [], {'max_length': '140', 'blank': 'True'})
        },
        u'storybase_story.storytemplatetranslation': {
            'Meta': {'object_name': 'StoryTemplateTranslation'},
            'best_for': ('storybase.fields.ShortTextField', [], {'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ingredients': ('storybase.fields.ShortTextField', [], {'blank': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'default': "'en'", 'max_length': '15'}),
            'story_template': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['storybase_story.StoryTemplate']"}),
            'tag_line': ('storybase.fields.ShortTextField', [], {'blank': 'True'}),
            'tip': ('storybase.fields.ShortTextField', [], {'blank': 'True'}),
            'title': ('storybase.fields.ShortTextField', [], {}),
            'translation_id': ('uuidfield.fields.UUIDField', [], {'unique': 'True', 'max_length': '32', 'blank': 'True'})
        },
        u'storybase_story.storytranslation': {
            'Meta': {'unique_together': "(('story', 'language'),)", 'object_name': 'StoryTranslation'},
            'call_to_action': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'connected_prompt': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'default': "'en'", 'max_length': '15'}),
            'story': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['storybase_story.Story']"}),
            'summary': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'title': ('storybase.fields.ShortTextField', [], {'blank': 'True'}),
            'translation_id': ('uuidfield.fields.UUIDField', [], {'unique': 'True', 'max_length': '32', 'blank': 'True'})
        },
        u'storybase_taxonomy.category': {
            'Meta': {'object_name': 'Category'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': u"orm['storybase_taxonomy.Category']"}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        u'storybase_taxonomy.tag': {
            'Meta': {'object_name': 'Tag'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100'}),
            'tag_id': ('uuidfield.fields.UUIDField', [], {'unique': 'True', 'max_length': '32', 'blank': 'True'})
        },
        u'storybase_taxonomy.taggeditem': {
            'Meta': {'object_name': 'TaggedItem'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'storybase_taxonomy_taggeditem_tagged_items'", 'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'items'", 'to': u"orm['storybase_taxonomy.Tag']"})
        },
        u'storybase_user.organization': {
            'Meta': {'object_name': 'Organization'},
            'contact_info': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'curated_stories': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'curated_in_organizations'", 'blank': 'True', 'through': u"orm['storybase_user.OrganizationStory']", 'to': u"orm['storybase_story.Story']"}),
            'featured_assets': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'featured_in_organizations'", 'blank': 'True', 'to': u"orm['storybase_asset.Asset']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_edited': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'members': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'organizations'", 'blank': 'True', 'through': u"orm['storybase_user.OrganizationMembership']", 'to': u"orm['auth.User']"}),
            'on_homepage': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'organization_id': ('uuidfield.fields.UUIDField', [], {'db_index': 'True', 'unique': 'True', 'max_length': '32', 'blank': 'True'}),
            'published': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "u'draft'", 'max_length': '10'}),
            'website_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        u'storybase_user.organizationmembership': {
            'Meta': {'object_name': 'OrganizationMembership'},
            'added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'member_type': ('django.db.models.fields.CharField', [], {'default': "'member'", 'max_length': '140'}),
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['storybase_user.Organization']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'storybase_user.organizationstory': {
            'Meta': {'object_name': 'OrganizationStory'},
            'added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['storybase_user.Organization']"}),
            'story': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['storybase_story.Story']"}),
            'weight': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'storybase_user.project': {
            'Meta': {'object_name': 'Project'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'curated_stories': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'curated_in_projects'", 'blank': 'True', 'through': u"orm['storybase_user.ProjectStory']", 'to': u"orm['storybase_story.Story']"}),
            'featured_assets': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'featured_in_projects'", 'blank': 'True', 'to': u"orm['storybase_asset.Asset']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_edited': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'members': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'projects'", 'blank': 'True', 'through': u"orm['storybase_user.ProjectMembership']", 'to': u"orm['auth.User']"}),
            'on_homepage': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'organizations': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'projects'", 'blank': 'True', 'to': u"orm['storybase_user.Organization']"}),
            'project_id': ('uuidfield.fields.UUIDField', [], {'db_index': 'True', 'unique': 'True', 'max_length': '32', 'blank': 'True'}),
            'published': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "u'draft'", 'max_length': '10'}),
            'website_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        u'storybase_user.projectmembership': {
            'Meta': {'object_name': 'ProjectMembership'},
            'added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'member_type': ('django.db.models.fields.CharField', [], {'default': "'member'", 'max_length': '140'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['storybase_user.Project']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'storybase_user.projectstory': {
            'Meta': {'object_name': 'ProjectStory'},
            'added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['storybase_user.Project']"}),
            'story': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['storybase_story.Story']"}),
            'weight': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['storybase_story']