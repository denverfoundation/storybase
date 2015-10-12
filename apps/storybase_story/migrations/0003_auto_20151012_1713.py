# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('storybase_asset', '0001_initial'),
        ('storybase_story', '0002_auto_20151012_1713'),
        ('storybase_taxonomy', '0001_initial'),
        ('storybase_help', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='story',
            name='tags',
            field=taggit.managers.TaggableManager(to='storybase_taxonomy.Tag', through='storybase_taxonomy.TaggedItem', blank=True, help_text='A comma-separated list of tags.', verbose_name='Tags'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='story',
            name='template_story',
            field=models.ForeignKey(related_name='template_for', blank=True, to='storybase_story.Story', help_text='Story whose structure was used to create this story', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='story',
            name='topics',
            field=models.ManyToManyField(related_name='stories', verbose_name='Topics', to='storybase_taxonomy.Category', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='sectiontranslation',
            name='section',
            field=models.ForeignKey(to='storybase_story.Section'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='sectiontranslation',
            unique_together=set([('section', 'language')]),
        ),
        migrations.AddField(
            model_name='sectionrelation',
            name='child',
            field=models.ForeignKey(related_name='section_parent', to='storybase_story.Section'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='sectionrelation',
            name='parent',
            field=models.ForeignKey(related_name='section_child', to='storybase_story.Section'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='sectionlayouttranslation',
            name='layout',
            field=models.ForeignKey(to='storybase_story.SectionLayout'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='sectionlayout',
            name='containers',
            field=models.ManyToManyField(related_name='layouts', to='storybase_story.Container', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='sectionasset',
            name='asset',
            field=models.ForeignKey(to='storybase_asset.Asset'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='sectionasset',
            name='container',
            field=models.ForeignKey(to='storybase_story.Container', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='sectionasset',
            name='section',
            field=models.ForeignKey(to='storybase_story.Section'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='sectionasset',
            unique_together=set([('section', 'container', 'weight')]),
        ),
        migrations.AddField(
            model_name='section',
            name='assets',
            field=models.ManyToManyField(related_name='sections', through='storybase_story.SectionAsset', to='storybase_asset.Asset', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='section',
            name='children',
            field=models.ManyToManyField(related_name='_parents', null=True, through='storybase_story.SectionRelation', to='storybase_story.Section', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='section',
            name='help',
            field=models.ForeignKey(to='storybase_help.Help', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='section',
            name='layout',
            field=models.ForeignKey(to='storybase_story.SectionLayout', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='section',
            name='story',
            field=models.ForeignKey(related_name='sections', to='storybase_story.Story'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='section',
            name='template_section',
            field=models.ForeignKey(related_name='template_for', blank=True, to='storybase_story.Section', help_text='A section that provides default values for layout, asset types and help for this section.', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='containertemplate',
            name='container',
            field=models.ForeignKey(to='storybase_story.Container'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='containertemplate',
            name='help',
            field=models.ForeignKey(blank=True, to='storybase_help.Help', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='containertemplate',
            name='section',
            field=models.ForeignKey(to='storybase_story.Section'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='containertemplate',
            name='template',
            field=models.ForeignKey(to='storybase_story.StoryTemplate'),
            preserve_default=True,
        ),
    ]
