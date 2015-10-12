# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import storybase_user.models
import storybase_asset.models
import storybase_badge.models
import storybase.fields
from django.conf import settings
import uuidfield.fields
import storybase.models.dirtyfields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('storybase_asset', '0001_initial'),
        ('storybase_badge', '0001_initial'),
        ('storybase_story', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.CharField(default='draft', max_length=10, choices=[('pending', 'pending'), ('draft', 'draft'), ('staged', 'staged'), ('published', 'published')])),
                ('published', models.DateTimeField(null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_edited', models.DateTimeField(auto_now=True)),
                ('organization_id', uuidfield.fields.UUIDField(auto=True, db_index=True)),
                ('slug', models.SlugField(blank=True)),
                ('contact_info', models.TextField(help_text='Contact information such as phone number and postal address for this Organization', verbose_name='contact information', blank=True)),
                ('website_url', models.URLField(verbose_name='Website URL', blank=True)),
                ('on_homepage', models.BooleanField(default=False, verbose_name='Featured on homepage')),
            ],
            options={
                'abstract': False,
            },
            bases=(storybase_user.models.PermissionBase, storybase_user.models.MembershipUtilsMixin, storybase_asset.models.FeaturedAssetsMixin, storybase_user.models.RecentStoriesMixin, storybase_user.models.FeaturedStoriesMixin, storybase.models.dirtyfields.DirtyFieldsMixin, models.Model),
        ),
        migrations.CreateModel(
            name='OrganizationMembership',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('member_type', models.CharField(default=b'member', max_length=140, choices=[(b'member', 'Member'), (b'owner', 'Owner')])),
                ('added', models.DateTimeField(auto_now_add=True)),
                ('organization', models.ForeignKey(to='storybase_user.Organization')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OrganizationStory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('weight', models.IntegerField(default=0)),
                ('added', models.DateTimeField(auto_now_add=True)),
                ('organization', models.ForeignKey(to='storybase_user.Organization')),
                ('story', models.ForeignKey(to='storybase_story.Story')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'story',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OrganizationTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_edited', models.DateTimeField(auto_now=True)),
                ('translation_id', uuidfield.fields.UUIDField(auto=True)),
                ('language', models.CharField(default=b'en', max_length=15, choices=[(b'en', b'English'), (b'es', b'Spanish')])),
                ('name', storybase.fields.ShortTextField(verbose_name='Organization Name')),
                ('description', models.TextField()),
                ('organization', models.ForeignKey(to='storybase_user.Organization')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.CharField(default='draft', max_length=10, choices=[('pending', 'pending'), ('draft', 'draft'), ('staged', 'staged'), ('published', 'published')])),
                ('published', models.DateTimeField(null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_edited', models.DateTimeField(auto_now=True)),
                ('project_id', uuidfield.fields.UUIDField(auto=True, db_index=True)),
                ('slug', models.SlugField(blank=True)),
                ('website_url', models.URLField(verbose_name='Website URL', blank=True)),
                ('on_homepage', models.BooleanField(default=False, verbose_name='Featured on homepage')),
            ],
            options={
                'abstract': False,
            },
            bases=(storybase_user.models.PermissionBase, storybase_user.models.MembershipUtilsMixin, storybase_asset.models.FeaturedAssetsMixin, storybase_user.models.RecentStoriesMixin, storybase_user.models.FeaturedStoriesMixin, storybase.models.dirtyfields.DirtyFieldsMixin, models.Model),
        ),
        migrations.CreateModel(
            name='ProjectMembership',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('member_type', models.CharField(default=b'member', max_length=140, choices=[(b'member', 'Member'), (b'owner', 'Owner')])),
                ('added', models.DateTimeField(auto_now_add=True)),
                ('project', models.ForeignKey(to='storybase_user.Project')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProjectStory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('weight', models.IntegerField(default=0)),
                ('added', models.DateTimeField(auto_now_add=True)),
                ('project', models.ForeignKey(to='storybase_user.Project')),
                ('story', models.ForeignKey(to='storybase_story.Story')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'story',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProjectTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('translation_id', uuidfield.fields.UUIDField(auto=True)),
                ('language', models.CharField(default=b'en', max_length=15, choices=[(b'en', b'English'), (b'es', b'Spanish')])),
                ('name', storybase.fields.ShortTextField(verbose_name='Project Name')),
                ('description', models.TextField()),
                ('project', models.ForeignKey(to='storybase_user.Project')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('profile_id', uuidfield.fields.UUIDField(auto=True, db_index=True)),
                ('notify_admin', models.BooleanField(default=True, help_text=b'Administrative account updates', verbose_name=b'Administrative Updates')),
                ('notify_digest', models.BooleanField(default=True, help_text=b'A weekly digest of Floodlight stories, events and new features', verbose_name=b'Weekly Digest')),
                ('notify_story_unpublished', models.BooleanField(default=True, help_text=b'Remind me to complete unpublished stories', verbose_name=b'Unpublished Story Reminder')),
                ('notify_story_published', models.BooleanField(default=True, help_text=b'Alert me when I publish a story', verbose_name=b'Published Story Notification')),
                ('notify_story_comment', models.BooleanField(default=True, help_text=b'Alert me when someone comments on one of my stories', verbose_name=b'Comment Notification')),
                ('badges', models.ManyToManyField(related_name='users', to='storybase_badge.Badge')),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(storybase_user.models.RecentStoriesMixin, models.Model, storybase_badge.models.BadgeEditor),
        ),
        migrations.AlterUniqueTogether(
            name='projecttranslation',
            unique_together=set([('project', 'language')]),
        ),
        migrations.AddField(
            model_name='project',
            name='curated_stories',
            field=models.ManyToManyField(related_name='curated_in_projects', through='storybase_user.ProjectStory', to='storybase_story.Story', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='project',
            name='featured_assets',
            field=models.ManyToManyField(help_text='Assets to be displayed in teaser version of this Project', related_name='featured_in_projects', to='storybase_asset.Asset', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='project',
            name='members',
            field=models.ManyToManyField(related_name='projects', through='storybase_user.ProjectMembership', to=settings.AUTH_USER_MODEL, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='project',
            name='organizations',
            field=models.ManyToManyField(related_name='projects', to='storybase_user.Organization', blank=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='organizationtranslation',
            unique_together=set([('organization', 'language')]),
        ),
        migrations.AddField(
            model_name='organization',
            name='curated_stories',
            field=models.ManyToManyField(related_name='curated_in_organizations', through='storybase_user.OrganizationStory', to='storybase_story.Story', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='organization',
            name='featured_assets',
            field=models.ManyToManyField(help_text='Assets to be displayed in teaser version of this Organization', related_name='featured_in_organizations', to='storybase_asset.Asset', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='organization',
            name='members',
            field=models.ManyToManyField(related_name='organizations', through='storybase_user.OrganizationMembership', to=settings.AUTH_USER_MODEL, blank=True),
            preserve_default=True,
        ),
    ]
