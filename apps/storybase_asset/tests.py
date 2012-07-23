import base64
from datetime import datetime
import hashlib
import mimetypes
import os

from django.conf import settings
from django.contrib.auth.models import User
from django.template.defaultfilters import striptags, truncatewords
from django.test import TestCase

from tastypie.test import ResourceTestCase, TestApiClient

from storybase.tests.base import FixedTestApiClient, FileCleanupMixin
from storybase_story.models import (create_section, create_story,
                                    Container, SectionAsset, SectionLayout)
from storybase_asset.models import (Asset, ExternalAsset, HtmlAsset,
    HtmlAssetTranslation, DataSet,
    create_html_asset, create_external_asset, create_local_image_asset,
    create_external_dataset)
from embedable_resource import EmbedableResource

class DataUrlMixin(object):
    """Mixin class for dealing with Data URLs"""
    def read_as_data_url(self, filename):
        """Read a file and return the file as a data URL"""
        (type, encoding) = mimetypes.guess_type(filename)
        with open(filename, "rb") as f:
            return "data:%s;base64, %s" % (type, base64.b64encode(f.read()))


class AssetModelTest(TestCase):
    def test_license_name(self):
        asset = HtmlAsset(license='CC BY')
        asset.save()
        translation = HtmlAssetTranslation(title="Test", asset=asset)
        translation.save()
        self.assertEqual(asset.license_name(), 'Attribution Creative Commons')

    def test_string_representation_from_title(self):
        """ Tests that the string representation of an Asset is the Asset's title """
        asset = HtmlAsset()
        asset.save()
        title = "Test Asset Title"
        translation = HtmlAssetTranslation(title=title, asset=asset)
        translation.save()
        self.assertEqual(unicode(asset), asset.title)

    def test_string_representation_from_asset_id(self):
        """ Tests that if a title is not specified, the string representation of the asset is based on the Asset ID """
        asset = HtmlAsset()
        asset.save()
        translation = HtmlAssetTranslation(asset=asset)
        translation.save()
        self.assertEqual(unicode(asset), "Asset %s" % asset.asset_id)

    def test_full_html_caption_nothing(self):
        """
        Test that full_html_caption() returns an empty string when there
        is no asset metadata to include in the caption
        """
        asset = create_html_asset(type='image', title='Test Asset')
        self.assertEqual(asset.full_caption_html(), '')

    def test_full_html_caption_caption_only(self):
        """
        Test that full_html_caption() includes the caption field text
        when there is only a caption to include in the caption
        """
        caption = "This is a test caption"
        asset = create_html_asset(type='image', title='Test Asset',
                                  caption=caption)
        self.assertIn(caption, asset.full_caption_html())

    def test_full_html_caption_attribution_only(self):
        """
        Test that full_html_caption() includes the attribution field text
        when there is only an attribution to include in the caption
        """
        attribution = "Some photographer"
        asset = create_html_asset(type='image', title='Test Asset',
                                  attribution=attribution)
        self.assertIn(attribution, asset.full_caption_html())

    def test_full_html_caption_attribution_caption(self):
        """
        Test that full_html_caption() includes both the caption and
        attribution field text when both are set 
        """
        attribution = "Some photographer"
        caption = "This is a test caption"
        asset = create_html_asset(type='image', title='Test Asset',
                                  attribution=attribution,
                                  caption=caption)
        self.assertIn(caption, asset.full_caption_html())
        self.assertIn(attribution, asset.full_caption_html())

    def test_dataset_html_nothing(self):
        """
        Test that dataset_html() returns nothing when there are no
        associated datasets
        """
        asset = create_html_asset(type='image', title='Test Asset')
        self.assertEqual(asset.dataset_html(), "")

    def test_dataset_html_one(self):
        """
        Test that dataset_html() lists a lone dataset associated
        with an Asset
        """
        dataset_title = ("Metro Denver Free and Reduced Lunch Trends by "
                         "School District")
        dataset_url = 'http://www.box.com/s/erutk9kacq6akzlvqcdr'
        asset = create_html_asset(type='image', title='Test Asset')
        dataset = create_external_dataset(
            title=dataset_title,
            url=dataset_url,
            source="Colorado Department of Education for Source",
            attribution="The Piton Foundation")
        asset.datasets.add(dataset)
        asset.save()
        self.assertIn(dataset_title, asset.dataset_html()) 
        self.assertIn(dataset_url, asset.dataset_html())

    def test_dataset_html_two(self):
        """
        Test that dataset_html() lists a lone dataset associated
        with an Asset
        """
        dataset_title1 = ("Metro Denver Free and Reduced Lunch Trends by "
                         "School District")
        dataset_url1 = 'http://www.box.com/s/erutk9kacq6akzlvqcdr'
        asset = create_html_asset(type='image', title='Test Asset')
        dataset1 = create_external_dataset(
            title=dataset_title1,
            url=dataset_url1,
            source="Colorado Department of Education for Source",
            attribution="The Piton Foundation")
        dataset_url2 = 'http://www.example.com/somedata.csv'
        dataset_title2 = "Test Dataset"
        dataset2 = create_external_dataset(
            title=dataset_title2,
            url=dataset_url2,
            source="Test Dataset Source",
            attribution="Test Dataset Hacker")
        asset.datasets.add(dataset1)
        asset.datasets.add(dataset2)
        asset.save()
        self.assertIn(dataset_title1, asset.dataset_html()) 
        self.assertIn(dataset_url1, asset.dataset_html())
        self.assertIn(dataset_title2, asset.dataset_html()) 
        self.assertIn(dataset_url2, asset.dataset_html())

    def test_dataset_html_download_text_links_to_file_true(self):
        """
        Test that dataset_html() has the correct interface text when the
        dataset URL points to a downloadable file.
        """
        dataset_title = ("Metro Denver Free and Reduced Lunch Trends by "
                         "School District")
        dataset_url = 'http://www.box.com/s/erutk9kacq6akzlvqcdr'
        asset = create_html_asset(type='image', title='Test Asset')
        dataset = create_external_dataset(
            title=dataset_title,
            url=dataset_url,
            source="Colorado Department of Education for Source",
            attribution="The Piton Foundation",
	    links_to_file=True)
        asset.datasets.add(dataset)
        asset.save()
        self.assertIn("Download the data", asset.dataset_html()) 

    def test_dataset_html_download_text_links_to_file_false(self):
        """
        Test that dataset_html() has the correct interface text when the
        dataset URL doesn't point to a downloadable file.
        """
        dataset_title = ("Metro Denver Free and Reduced Lunch Trends by "
                         "School District")
        dataset_url = 'http://www.box.com/s/erutk9kacq6akzlvqcdr'
        asset = create_html_asset(type='image', title='Test Asset')
        dataset = create_external_dataset(
            title=dataset_title,
            url=dataset_url,
            source="Colorado Department of Education for Source",
            attribution="The Piton Foundation",
	    links_to_file=False)
        asset.datasets.add(dataset)
        asset.save()
        self.assertIn("View the data", asset.dataset_html()) 

    def test_full_html_caption_dataset_only(self):
        """
        Test that full_html_caption() includes listed datasets
        when only datasets are associated with an asset
        """
        asset = create_html_asset(type='image', title='Test Asset')
        dataset_title = ("Metro Denver Free and Reduced Lunch Trends by "
                         "School District")
        dataset_url = 'http://www.box.com/s/erutk9kacq6akzlvqcdr'
        dataset = create_external_dataset(
            title=dataset_title,
            url=dataset_url,
            source="Colorado Department of Education for Source",
            attribution="The Piton Foundation")
        asset.datasets.add(dataset)
        asset.save()
        self.assertIn(dataset_title, asset.full_caption_html())


class HtmlAssetModelTest(TestCase):
    def test_string_representation_from_title(self):
        """ Tests that the string representation of an Html Asset is autogenerated from the Body field when no title is present """ 
        asset = HtmlAsset()
        asset.save()
        body = "Eboney Brown's kids range from age one to age nine, so it helps that her daycare center, Early Excellence, is just a short walk from Wyatt-Edison Charter School, where her older kids go. Early Excellence, which welcomes guests with a mural of a white Denver skyline set against a backdrop of blue mountains, serves families from as far away as Thornton and Green Valley Ranch. And many of those families, says Early Excellence director Jennifer Luke, are caught in a cycle of poverty and depend daily on regional transportation. \"I know they can't put a bus on every corner,\" says Luke, who knows many parents who combine public transportation with long walks - year round, no matter the weather."
        translation = HtmlAssetTranslation(body=body, asset=asset)
        translation.save()
        self.assertEqual(unicode(asset), truncatewords(striptags(asset.body), 4))

    def test_display_title_with_no_explicit_title(self):
        """ Tests that the display_title() method returns an automatically
        generated title when an explicit title isn't set

        """
        asset = HtmlAsset()
        asset.save()
        body = "Eboney Brown's kids range from age one to age nine, so it helps that her daycare center, Early Excellence, is just a short walk from Wyatt-Edison Charter School, where her older kids go. Early Excellence, which welcomes guests with a mural of a white Denver skyline set against a backdrop of blue mountains, serves families from as far away as Thornton and Green Valley Ranch. And many of those families, says Early Excellence director Jennifer Luke, are caught in a cycle of poverty and depend daily on regional transportation. \"I know they can't put a bus on every corner,\" says Luke, who knows many parents who combine public transportation with long walks - year round, no matter the weather."
        translation = HtmlAssetTranslation(body=body, asset=asset)
        translation.save()
        self.assertEqual(asset.display_title(),
                         truncatewords(striptags(asset.body), 4))

class EmbedableResourceTest(TestCase):
    def test_get_google_spreadsheet_embed(self):
        url = 'https://docs.google.com/spreadsheet/pub?key=0As2exFJJWyJqdDhBejVfN1RhdDg2b0QtYWR4X2FTZ3c&output=html' 
        expected = "<iframe width='500' height='300' frameborder='0' src='%s&widget=true'></iframe>" % url
        self.assertEqual(EmbedableResource.get_html(url), expected)

class AssetApiTest(FileCleanupMixin, TestCase):
    """ Test the public API for creating Assets """

    def test_create_html_asset(self):
        """ Test create_html_asset() """

        title = "Success Express"
        type = "quotation"
        attribution = "Ed Brennan, EdNews Colorado"
        source_url = "http://www.ednewsparent.org/teaching-learning/5534-denvers-success-express-rolls-out-of-the-station"
        asset_created = datetime.strptime('2011-06-03 00:00',
                                          '%Y-%m-%d %H:%M')
        status='published'
        body = """
        In both the Far Northeast and the Near Northeast, school buses 
        will no longer make a traditional series of stops in neighborhoods
        - once in the morning and once in the afternoon. Instead, a fleet
        of DPS buses will circulate between area schools, offering students
        up to three chances to catch the one that will get them to their
        school of choice on time.

        Martha Carranza, who has a child at Bruce Randolph, said that for
        students who have depended on RTD, "I was very worried because it
        is very dangerous for the children coming from Globeville and also
        from Swansea ... the kids were arriving late and sometimes missing
        classes altogether."

        And, said Carranza, "... we are very happy that with the new
        transportation system, no child will have any excuse to miss 
        school."
        """
        asset = create_html_asset(type, title, caption='', body=body,
            attribution=attribution, source_url=source_url, status=status,
            asset_created=asset_created)
        self.assertEqual(asset.title, title)
        self.assertEqual(asset.type, type)
        self.assertEqual(asset.attribution, attribution)
        self.assertEqual(asset.source_url, source_url)
        self.assertEqual(asset.asset_created, asset_created)
        self.assertEqual(asset.status, status)
        retrieved_asset = HtmlAsset.objects.get(pk=asset.pk)
        self.assertEqual(retrieved_asset.title, title)
        self.assertEqual(retrieved_asset.type, type)
        self.assertEqual(retrieved_asset.attribution, attribution)
        self.assertEqual(retrieved_asset.source_url, source_url)
        self.assertEqual(retrieved_asset.asset_created, asset_created)
        self.assertEqual(retrieved_asset.status, status)

    def test_create_external_asset(self):
        """ Test create_external_asset() """
        title = 'Large Flock of birds in pomona, CA'
        type = 'video'
        caption = 'An intense flock of birds outside a theater in Pomona, CA'
        asset_created = datetime.strptime('2007-04-11 00:00',
                                          '%Y-%m-%d %H:%M')
        url = 'http://www.youtube.com/watch?v=BJQycHkddhA'
        attribution = 'Geoffrey Hing'
        asset = create_external_asset(
            type,
            title,
            caption,
            url,
            asset_created=asset_created,
            attribution=attribution)
        self.assertEqual(asset.title, title)
        self.assertEqual(asset.type, type)
        self.assertEqual(asset.caption, caption)
        self.assertEqual(asset.asset_created, asset_created)
        self.assertEqual(asset.attribution, attribution)
        retrieved_asset = ExternalAsset.objects.get(pk=asset.pk)
        self.assertEqual(retrieved_asset.title, title)
        self.assertEqual(retrieved_asset.type, type)
        self.assertEqual(retrieved_asset.caption, caption)
        self.assertEqual(retrieved_asset.asset_created, asset_created)
        self.assertEqual(retrieved_asset.attribution, attribution)

    def test_create_local_image_asset(self):
        """Test creating a LocalImageAsset model instance"""
        asset_type = 'image'
        asset_title = "Test Image Asset"
        asset_caption = "This is a test image"
        image_filename = "test_image.jpg"

        app_dir = os.path.dirname(os.path.abspath(__file__))
        img_path = os.path.join(app_dir, "test_files", image_filename)
        with open(img_path) as image:
            original_hash = hashlib.sha1(image.read()).digest()
            asset = create_local_image_asset(
                type=asset_type,
                image=image,
                image_filename="test_image.jpg",
                title=asset_title,
                caption=asset_caption)
            self.add_file_to_cleanup(asset.image.file.path)
            copy_hash = hashlib.sha1(file(asset.image.file.path, 'r').read()).digest()
            # Verify that the 2 files are the same
            self.assertEqual(original_hash, copy_hash)
            # Verify the metadata is the same
            self.assertEqual(asset.title, asset_title)
            self.assertEqual(asset.type, asset_type)
            self.assertEqual(asset.caption, asset_caption)


class DataSetResourceTest(DataUrlMixin, FileCleanupMixin, ResourceTestCase):
    def setUp(self):
        super(DataSetResourceTest, self).setUp()
        self.api_client = TestApiClient()
        self.username = 'test'
        self.password = 'test'
        self.user = User.objects.create_user(self.username, 
            'test@example.com', self.password)

    def test_post_list_file(self):
        data_filename = "test_data.csv"
        app_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(app_dir, "test_files", data_filename)
        original_hash = hashlib.sha1(file(data_path, 'r').read()).digest()
        encoded_file = self.read_as_data_url(data_path)

        post_data = {
            'title': "Test Dataset",
            'description': "A test dataset",
            'file': encoded_file,
            'filename': data_filename,
            'language': "en",
        }
        self.assertEqual(DataSet.objects.count(), 0)
        self.api_client.client.login(username=self.username,
                                     password=self.password)
        uri = '/api/0.1/datasets/';
        resp = self.api_client.post(uri, format='json', data=post_data)
        self.assertHttpCreated(resp)
        self.assertEqual(DataSet.objects.count(), 1)
        # Compare the response data with the post data
        self.assertEqual(self.deserialize(resp)['title'], 
                         post_data['title'])
        self.assertEqual(self.deserialize(resp)['description'], 
                         post_data['description'])
        # Compare the created model instance with the post data
        created_dataset = DataSet.objects.get_subclass()
        self.assertEqual(created_dataset.title, post_data['title'])
        self.assertEqual(created_dataset.description, post_data['description'])
        # Compare the uploaded file and the original 
        created_hash = hashlib.sha1(
            file(created_dataset.file.path, 'r').read()).digest()
        self.assertEqual(original_hash, created_hash)
        # Set our created file to be cleaned up
        self.add_file_to_cleanup(created_dataset.file.file.path)

    def test_post_list_url(self):
        post_data = {
            'title': "Test Dataset",
            'description': "A test dataset",
            'url': 'https://data.cityofchicago.org/Transportation/Chicago-Street-Names/i6bp-fvbx',
            'links_to_file': False,
            'language': "en",
        }
        self.assertEqual(DataSet.objects.count(), 0)
        self.api_client.client.login(username=self.username,
                                     password=self.password)
        uri = '/api/0.1/datasets/';
        resp = self.api_client.post(uri, format='json', data=post_data)
        self.assertHttpCreated(resp)
        self.assertEqual(DataSet.objects.count(), 1)
        # Compare the response data with the post data
        self.assertEqual(self.deserialize(resp)['title'], 
                         post_data['title'])
        self.assertEqual(self.deserialize(resp)['description'], 
                         post_data['description'])
        self.assertEqual(self.deserialize(resp)['url'], 
                         post_data['url'])
        self.assertEqual(self.deserialize(resp)['links_to_file'], 
                         post_data['links_to_file'])
        # Compare the created model instance with the post data
        created_dataset = DataSet.objects.get_subclass()
        self.assertEqual(created_dataset.title, post_data['title'])
        self.assertEqual(created_dataset.description, post_data['description'])
        self.assertEqual(created_dataset.url, post_data['url'])
        self.assertEqual(created_dataset.links_to_file, post_data['links_to_file'])

    def test_post_list_unauthorized(self):
        """Test that an unauthenticated user can't create a dataset"""
        post_data = {
            'title': "Test Dataset",
            'description': "A test dataset",
            'url': 'https://data.cityofchicago.org/Transportation/Chicago-Street-Names/i6bp-fvbx',
            'links_to_file': False,
            'language': "en",
        }
        self.assertEqual(DataSet.objects.count(), 0)
        uri = '/api/0.1/datasets/';
        resp = self.api_client.post(uri, format='json', data=post_data)
        self.assertHttpUnauthorized(resp)
        self.assertEqual(DataSet.objects.count(), 0)


class DataSetApiTest(TestCase):
    """ Test the public API for creating DataSets """

    def test_create_external_dataset(self):
        """Test create_external_dataset()"""
        user = User.objects.create(username='admin')
        url = 'http://www.box.com/s/erutk9kacq6akzlvqcdr'
        title = ("Metro Denver Free and Reduced Lunch Trends by School "
                 "District")
        source = "Colorado Department of Education for Source"
        attribution = "The Piton Foundation"
        dataset = create_external_dataset(title=title, url=url, 
                                          source=source, 
                                          attribution=attribution,
                                          owner=user)
        self.assertEqual(dataset.title, title)
        self.assertEqual(dataset.download_url(), url)
        self.assertEqual(dataset.owner, user)
        self.assertEqual(dataset.source, source)
        self.assertEqual(dataset.attribution, attribution)


class AssetPermissionTest(TestCase):
    def setUp(self):
        from django.contrib.auth.models import Group
        self.admin_group = Group.objects.create(name=settings.ADMIN_GROUP_NAME)
        self.user1 = User.objects.create_user("test1", "test1@example.com",
                                              "test1")
        self.user2 = User.objects.create_user("test2", "test2@example.com",
                                              "test2")
        self.asset = create_html_asset(type='image', title='Test Asset',
                                       owner=self.user1)


    def test_user_can_add(self):
        """Test that a user has permission to add an asset"""
        self.assertTrue(self.asset.user_can_add(self.user1))

    def test_user_can_add_inactive(self):
        """Test that an inactive user can't add an asset"""
        self.assertTrue(self.asset.user_can_add(self.user1))
        self.user1.is_active = False 
        self.assertFalse(self.asset.user_can_add(self.user1))

    def test_user_can_change_as_owner(self):
        """Test that owner has permissions to change their asset"""
        self.assertTrue(self.asset.user_can_change(self.user1))

    def test_user_can_change_not_author(self):
        """Test that a owner doesn't have permissions to change another user's asset"""
        self.assertFalse(self.asset.user_can_change(self.user2))

    def test_user_can_change_superuser(self):
        """Test that a superuser can change another user's asset"""
        self.assertFalse(self.asset.user_can_change(self.user2))
        self.user2.is_superuser = True
        self.user2.save()
        self.assertTrue(self.asset.user_can_change(self.user2))

    def test_user_can_change_admin(self):
        """Test that a member of the admin group can change another user's asset"""
        self.assertFalse(self.asset.user_can_change(self.user2))
        self.user2.groups.add(self.admin_group)
        self.user2.save()
        self.assertTrue(self.asset.user_can_change(self.user2))

    def test_user_can_change_inactive(self):
        """Test that an inactive user can't change their own story"""
        self.assertTrue(self.asset.user_can_change(self.user1))
        self.user1.is_active = False 
        self.assertFalse(self.asset.user_can_change(self.user1))


class AssetResourceTest(DataUrlMixin, FileCleanupMixin, ResourceTestCase):
    fixtures = ['section_layouts.json']
    
    def get_obj(self, objects, obj_id_field, obj_id):
        for obj in objects:
            if obj[obj_id_field] == obj_id:
                return obj

    def get_response_asset(self, resp, asset_id):
        return self.get_obj(self.deserialize(resp)['objects'], 'asset_id', 
                            asset_id)

    def setUp(self):
        super(AssetResourceTest, self).setUp()
        # Use our fixed TestApiClient instead of the default
        self.api_client = FixedTestApiClient()
        self.username = 'test'
        self.password = 'test'
        self.user = User.objects.create_user(self.username, 'test@example.com', self.password)
        self.user2 = User.objects.create_user("test2", "test2@example.com",
                                              "test2")

    def test_get_list(self):
        """Test getting a list of assets in the system"""
        asset1 = create_html_asset(type='text', title='Test Html Asset',
                                   body='<p>Test body</p>',
                                   attribution="Jane Doe", 
                                   status="published",
                                   owner=self.user)
        asset2 = create_external_asset(type='image', 
                                       title='Test External Asset',
                                       url="http://example.com/image.jpg",
                                       status="published", owner=self.user)
        uri = '/api/0.1/assets/'
        resp = self.api_client.get(uri)
        self.assertValidJSONResponse(resp)
        self.assertEqual(len(self.deserialize(resp)['objects']), 2)
        asset_ids = [asset['asset_id'] for asset 
                     in self.deserialize(resp)['objects']]
        self.assertIn(asset1.asset_id, asset_ids)
        self.assertIn(asset2.asset_id, asset_ids)
        self.assertEqual(self.get_response_asset(resp, asset1.asset_id)['body'],
                         asset1.body)
        self.assertEqual(self.get_response_asset(resp, asset2.asset_id)['url'],
                         asset2.url)

    def test_get_list_published_only(self):
        """Test that unauthenticated users see only published assets"""
        asset1 = create_html_asset(type='text', title='Test Html Asset',
                                   body='<p>Test body</p>',
                                   attribution="Jane Doe", 
                                   status="published",
                                   owner=self.user)
        asset2 = create_external_asset(type='image', 
                                       title='Test External Asset',
                                       url="http://example.com/image.jpg",
                                       status="draft", owner=self.user)
        uri = '/api/0.1/assets/'
        resp = self.api_client.get(uri)
        self.assertValidJSONResponse(resp)
        self.assertEqual(len(self.deserialize(resp)['objects']), 1)
        self.assertEqual(self.deserialize(resp)['objects'][0]['asset_id'],
                         asset1.asset_id)

    def test_get_list_published_drafts(self):
        """Test that a user's own unpublished assets appear in the list"""
        asset1 = create_html_asset(type='text', title='Test Html Asset',
                                   body='<p>Test body</p>',
                                   attribution="Jane Doe", 
                                   status="draft",
                                   owner=self.user)
        self.api_client.client.login(username=self.username, password=self.password)
        uri = '/api/0.1/assets/'
        resp = self.api_client.get(uri)
        self.assertValidJSONResponse(resp)
        self.assertEqual(len(self.deserialize(resp)['objects']), 1)
        self.assertEqual(self.deserialize(resp)['objects'][0]['asset_id'],
                         asset1.asset_id)

    def test_get_detail_image(self):
        """Test getting the details for a locally-stored image asset"""
        asset_type = 'image'
        asset_title = "Test Image Asset"
        asset_caption = "This is a test image"
        image_filename = "test_image.jpg"

        app_dir = os.path.dirname(os.path.abspath(__file__))
        img_path = os.path.join(app_dir, "test_files", image_filename)
        with open(img_path) as image:
            asset = create_local_image_asset(
                type=asset_type,
                image=image,
                image_filename=image_filename,
                title=asset_title,
                caption=asset_caption,
                status='published')
            self.add_file_to_cleanup(asset.image.file.path)
            uri = '/api/0.1/assets/%s/' % (asset.asset_id)
            resp = self.api_client.get(uri)
            self.assertValidJSONResponse(resp)
            self.assertEqual(os.path.basename(self.deserialize(resp)['image']),
                             image_filename)
            self.assertEqual(self.deserialize(resp)['type'], asset_type)
            self.assertEqual(self.deserialize(resp)['title'], asset_title)
            self.assertEqual(self.deserialize(resp)['caption'], asset_caption)
            self.assertIn('<img src', self.deserialize(resp)['content'])

    def test_post_list_image(self):
        """Test creating a asset with the data stored in an uploaded image"""
        image_filename = "test_image.jpg"

        app_dir = os.path.dirname(os.path.abspath(__file__))
        img_path = os.path.join(app_dir, "test_files", image_filename)
        original_hash = hashlib.sha1(file(img_path, 'r').read()).digest()
        encoded_file = self.read_as_data_url(img_path)
        post_data = {
            'type': "image",
            'title': "Test Image Asset",
            'caption': "This is a test image",
            'status': "published",
            'image': encoded_file,
            'filename': image_filename,
            'language': "en",
        }
        self.assertEqual(Asset.objects.count(), 0)
        self.api_client.client.login(username=self.username,
                                     password=self.password)
        resp = self.api_client.post('/api/0.1/assets/',
                               format='json', data=post_data)
        self.assertHttpCreated(resp)
        # Check that asset was created in the system and has the correct
        # metadata
        self.assertEqual(Asset.objects.count(), 1)
        created_asset = Asset.objects.get_subclass()
        self.assertEqual(created_asset.type, post_data['type'])
        self.assertEqual(created_asset.title, post_data['title'])
        self.assertEqual(created_asset.caption, post_data['caption'])
        self.assertEqual(created_asset.status, post_data['status'])
        self.assertEqual(created_asset.get_languages(),
                         [post_data['language']])
        self.assertEqual(created_asset.owner, self.user)
        # Check that the id is returned by the endpoint
        returned_asset_id = resp['location'].split('/')[-2]
        self.assertEqual(created_asset.asset_id, returned_asset_id)
        # Compare the uploaded image and the original 
        created_hash = hashlib.sha1(file(created_asset.image.path, 'r').read()).digest()
        self.assertEqual(original_hash, created_hash)
        # Set our created file to be cleaned up
        self.add_file_to_cleanup(created_asset.image.file.path)


    def test_post_list_html(self):
        """Test creating an HTML asset"""
        post_data = {
            'title' : "Success Express",
            'type': "quotation",
            'attribution': "Ed Brennan, EdNews Colorado",
            'status': 'published',
            'body': """
            In both the Far Northeast and the Near Northeast, school buses 
            will no longer make a traditional series of stops in neighborhoods
            - once in the morning and once in the afternoon. Instead, a fleet
            of DPS buses will circulate between area schools, offering students
            up to three chances to catch the one that will get them to their
            school of choice on time.

            Martha Carranza, who has a child at Bruce Randolph, said that for
            students who have depended on RTD, "I was very worried because it
            is very dangerous for the children coming from Globeville and also
            from Swansea ... the kids were arriving late and sometimes missing
            classes altogether."

            And, said Carranza, "... we are very happy that with the new
            transportation system, no child will have any excuse to miss 
            school."
            """,
            'language': "en",
        }
        self.assertEqual(Asset.objects.count(), 0)
        self.api_client.client.login(username=self.username, password=self.password)
        response = self.api_client.post('/api/0.1/assets/',
                               format='json', data=post_data)
        self.assertHttpCreated(response)
        self.assertEqual(Asset.objects.count(), 1)
        created_asset = Asset.objects.get_subclass()
        self.assertEqual(created_asset.type, post_data['type'])
        self.assertEqual(created_asset.title, post_data['title'])
        self.assertEqual(created_asset.attribution, post_data['attribution'])
        self.assertEqual(created_asset.status, post_data['status'])

    def test_post_list_url(self):
        """Test creating an asset for externally-hosted content"""
        post_data = {
            'title': 'Large Flock of birds in pomona, CA',
            'type': 'video',
            'caption': 'An intense flock of birds outside a theater in Pomona, CA',
            'url': 'http://www.youtube.com/watch?v=BJQycHkddhA',
            'attribution': 'Geoffrey Hing',
        }
        self.assertEqual(Asset.objects.count(), 0)
        self.api_client.client.login(username=self.username, password=self.password)
        resp = self.api_client.post('/api/0.1/assets/',
                               format='json', data=post_data)
        self.assertEqual(self.deserialize(resp)['title'], 
                         post_data['title'])
        self.assertEqual(self.deserialize(resp)['type'], 
                         post_data['type'])
        self.assertEqual(self.deserialize(resp)['caption'], 
                         post_data['caption'])
        self.assertEqual(self.deserialize(resp)['url'], 
                         post_data['url'])
        self.assertEqual(self.deserialize(resp)['attribution'], 
                         post_data['attribution'])
        self.assertIn("iframe", self.deserialize(resp)['content']) 
        self.assertHttpCreated(resp)
        self.assertEqual(Asset.objects.count(), 1)
        created_asset = Asset.objects.get_subclass()
        self.assertEqual(created_asset.title, post_data['title'])
        self.assertEqual(created_asset.type, post_data['type'])
        self.assertEqual(created_asset.caption, post_data['caption'])
        self.assertEqual(created_asset.attribution, post_data['attribution'])
        self.assertEqual(created_asset.url, post_data['url'])

    def test_put_detail_html(self):
        asset = create_html_asset(type='text', title='Test Html Asset',
                                   body='<p>Test body</p>',
                                   attribution="Jane Doe", 
                                   status="published",
                                   owner=self.user)
        data = {
            'body': 'New Body'
        }
        self.api_client.client.login(username=self.username, password=self.password)
        response = self.api_client.put('/api/0.1/assets/%s/' % (asset.asset_id),
                               format='json', data=data)
        self.assertHttpAccepted(response)
        modified_asset = Asset.objects.select_subclasses().get(asset_id=asset.asset_id)
        self.assertEqual(modified_asset.body, data['body'])

    def test_get_list_for_story(self):
        """Test getting only a single story's assets"""
        story = create_story(title="Test Story", summary="Test Summary",
                             byline="Test Byline", status="published",
                             language="en", author=self.user)
        asset1 = create_html_asset(type='text', title='Test Html Asset',
                                   body='<p>Test body</p>',
                                   attribution="Jane Doe", 
                                   status="published",
                                   owner=self.user)
        asset2 = create_external_asset(type='image', 
                                       title='Test External Asset',
                                       url="http://example.com/image.jpg",
                                       status="published", owner=self.user)
        asset3 = create_html_asset(type='text', title='Test Html Asset 2',
                                   body='<p>Test body 2</p>',
                                   attribution="Jane Doe", 
                                   status="published",
                                   owner=self.user)
        story.assets = [asset1, asset2]
        self.assertEqual(story.assets.count(), 2)
        uri = '/api/0.1/assets/stories/%s/' % (story.story_id)
        resp = self.api_client.get(uri)
        self.assertValidJSONResponse(resp)
        self.assertEqual(len(self.deserialize(resp)['objects']), 2)
        asset_ids = [asset['asset_id'] for asset 
                     in self.deserialize(resp)['objects']]
        self.assertIn(asset1.asset_id, asset_ids)
        self.assertIn(asset2.asset_id, asset_ids)
        self.assertNotIn(asset3.asset_id, asset_ids)

    def test_get_list_for_section(self):
        """Test getting assets for a single section"""
        story = create_story(title="Test Story", summary="Test Summary",
                             byline="Test Byline", status="published",
                             language="en", author=self.user)
        layout = SectionLayout.objects.get(sectionlayouttranslation__name="Side by Side")
        container1 = Container.objects.get(name='left')
        container2 = Container.objects.get(name='right')
        section = create_section(title="Test Section 1", story=story,
                                  layout=layout)
        asset1 = create_html_asset(type='text', title='Test Asset',
                                   body='Test content',
                                   owner=self.user, status='published')
        asset2 = create_html_asset(type='text', title='Test Asset 2',
                                   body='Test content 2',
                                   owner=self.user, status='published')
        asset3 = create_html_asset(type='text', title='Test Asset 3',
                                   body='Test content 3',
                                   owner=self.user, status='published')
        story2 = create_story(title="Test Story 2", summary="Test Summary",
                             byline="Test Byline", status="published",
                             language="en", author=self.user)
        section2 = create_section(title="Test Section 2", story=story2,
                                  layout=layout)
        SectionAsset.objects.create(section=section, asset=asset1, container=container1)
        SectionAsset.objects.create(section=section, asset=asset2, container=container2)
        SectionAsset.objects.create(section=section2, asset=asset3, container=container1)
        uri = '/api/0.1/assets/sections/%s/' % (section.section_id)
            
        resp = self.api_client.get(uri)
        self.assertValidJSONResponse(resp)
        self.assertEqual(len(self.deserialize(resp)['objects']), 2)
        self.assertEqual(
            self.deserialize(resp)['objects'][0]['asset_id'],
            asset1.asset_id)
        self.assertEqual(
            self.deserialize(resp)['objects'][1]['asset_id'],
            asset2.asset_id)
        self.assertEqual(
            self.deserialize(resp)['objects'][0]['type'],
            asset1.type)
        self.assertEqual(
            self.deserialize(resp)['objects'][1]['type'],
            asset2.type)
        self.assertEqual(
            self.deserialize(resp)['objects'][0]['title'],
            asset1.title)
        self.assertEqual(
            self.deserialize(resp)['objects'][1]['title'],
            asset2.title)

    def test_get_list_no_section(self):
        """
        Test getting assets for a story that are not associated with a section
        """
        story = create_story(title="Test Story", summary="Test Summary",
                             byline="Test Byline", status="published",
                             language="en", author=self.user)
        layout = SectionLayout.objects.get(sectionlayouttranslation__name="Side by Side")
        container1 = Container.objects.get(name='left')
        container2 = Container.objects.get(name='right')
        section = create_section(title="Test Section 1", story=story,
                                  layout=layout)
        asset1 = create_html_asset(type='text', title='Test Asset',
                                   body='Test content',
                                   owner=self.user, status='published')
        asset2 = create_html_asset(type='text', title='Test Asset 2',
                                   body='Test content 2',
                                   owner=self.user, status='published')
        asset3 = create_html_asset(type='text', title='Test Asset 3',
                                   body='Test content 3',
                                   owner=self.user, status='published')
        SectionAsset.objects.create(section=section, asset=asset1, container=container1)
        SectionAsset.objects.create(section=section, asset=asset2, container=container2)
        story.assets.add(asset3)
        story.save()
        uri = '/api/0.1/assets/stories/%s/sections/none/' % (story.story_id)
            
        resp = self.api_client.get(uri)
        self.assertValidJSONResponse(resp)
        self.assertEqual(len(self.deserialize(resp)['objects']), 1)
        self.assertEqual(
            self.deserialize(resp)['objects'][0]['asset_id'],
            asset3.asset_id)
        self.assertEqual(
            self.deserialize(resp)['objects'][0]['type'],
            asset3.type)
        self.assertEqual(
            self.deserialize(resp)['objects'][0]['title'],
            asset3.title)
