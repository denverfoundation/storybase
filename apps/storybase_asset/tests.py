import base64
from datetime import datetime
import hashlib
from itertools import ifilter
import mimetypes
import os

import django
from django.conf import settings
from django.contrib.auth.models import User
from django.template.defaultfilters import striptags, truncatewords
from django.test import TestCase
from django.test.client import encode_multipart, BOUNDARY, MULTIPART_CONTENT

from tastypie.test import ResourceTestCase, TestApiClient

from storybase.tests.base import FixedTestApiClient, FileCleanupMixin
from storybase_story.models import (create_section, create_story,
    Container, SectionAsset, SectionLayout, Story)
from storybase_asset.models import (Asset, ExternalAsset, HtmlAsset,
    HtmlAssetTranslation, ExternalDataSet, DataSet,
    create_html_asset, create_external_asset, create_local_image_asset,
    create_external_dataset, create_local_dataset)
from storybase_asset.oembed.providers import GoogleSpreadsheetProvider
from storybase_asset.utils import image_type_supported

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
        dataset_url = 'http://floodlightproject.org/test_data.csv'
        asset = create_html_asset(type='image', title='Test Asset')
        dataset = create_external_dataset(
            title=dataset_title,
            url=dataset_url,
            source="Colorado Department of Education for Source",
            attribution="The Piton Foundation",
	    )
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
	    )
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

    def test_datasets_added_to_story(self):
        """
        Test that adding a dataset to an asset also adds it to the assets'
        stories.
        """
        asset = create_html_asset(type='image', title='Test Asset')
        story = create_story(title="Test Story", summary="Test Summary",
            byline="Test Byline", status="published", language="en")
        story.assets.add(asset)
        dataset_title = ("Metro Denver Free and Reduced Lunch Trends by "
                         "School District")
        dataset_url = 'http://www.box.com/s/erutk9kacq6akzlvqcdr'
        dataset = create_external_dataset(
            title=dataset_title,
            url=dataset_url,
            source="Colorado Department of Education for Source",
            attribution="The Piton Foundation")
        asset.datasets.add(dataset)
        self.assertIn(dataset, story.datasets.select_subclasses())


class ExternalAssetModelTest(TestCase):
    def test_get_oembed_response_youtube_short(self):
        """
        Test getting an oembed response for a YouTube URL of the form
        http://youtu.be/KpichyyCutw

        """
        url = 'http://youtu.be/KpichyyCutw'
        response_data = ExternalAsset.get_oembed_response(url)
        self.assertIn('html', response_data)

    def test_get_oembed_response_soundcloud(self):
        """
        Test getting an oembed response for a SoundCloud URL 
        """
        # Long URL
        url = 'http://soundcloud.com/inews/long-term-care-for-kcfr-public-radio-day-1' 
        response_data = ExternalAsset.get_oembed_response(url)
        self.assertIn('html', response_data)
        # Short URL
        url = 'http://snd.sc/18NoosH'
        response_data = ExternalAsset.get_oembed_response(url)
        self.assertIn('html', response_data)

    def test_string_representation_from_url_truncated(self):
        """Test that auto-generated string representations are truncated"""
        url = "https://mail-attachment.googleusercontent.com/attachment/u/0/?ui=2&ik=7d10e7106d&view=att&th=139b9764517f43f5&attid=0.1&disp=inline&realattid=f_h704ppby0&safe=1&zw&saduie=AG9B_P-RVclBuCVY_NPm9GOGWp3O&sadet=1347459925218&sads=MMfkFunUT4iL-5L1SpqALCfYLGg&sadssc=1"
        asset = create_external_asset(type='image', title='', url=url)
        self.assertEqual(len(asset.__unicode__()), 100)

    def test_get_thumbnail_url_image_no_oembed(self):
        """
        Test that the raw URL of an image is returned when there's no
        oEmbed provider for the URL.
        """
        url = 'http://fakedomain.com/uploads/image.jpg'
        asset = create_external_asset(type='image', title='', url=url)
        self.assertEqual(asset.get_thumbnail_url(), url)

    def test_get_thumbnail_url_video_no_oembed(self):
        """
        Test that None is returned when there's no oEmbed provider for
        a URL and the asset's type is not image.
        """
        url = 'http://fakedomain.com/uploads/video.m4v'
        asset = create_external_asset(type='video', title='', url=url)
        self.assertEqual(asset.get_thumbnail_url(), None)

    def test_url_is_image_file(self):
        asset = create_external_asset(type='image', title='',
            url='http://fakedomain.com/files/image.png')
        self.assertTrue(asset.url_is_image_file())
        asset = create_external_asset(type='image', title='',
            url='http://fakedomain.com/files/image.jpg')
        self.assertTrue(asset.url_is_image_file())
        asset = create_external_asset(type='image', title='',
            url='http://fakedomain.com/files/image.gif')
        self.assertTrue(asset.url_is_image_file())
        asset = create_external_asset(type='image', title='',
            url='http://fakedomain.com/files/image.svg')
        self.assertTrue(asset.url_is_image_file())
        asset = create_external_asset(type='image', title='',
            url='http://fakedomain.com/files/image.bmp')
        self.assertTrue(asset.url_is_image_file())
        asset = create_external_asset(type='text', title='',
            url='http://fakedomain.com/files/readme.txt')
        self.assertFalse(asset.url_is_image_file())

    def test_css_classes(self):
        asset = create_external_asset(type='video', title='',
                url='http://youtu.be/KpichyyCutw')
        css_classes = asset.css_classes()
        self.assertIn('asset-type-video', css_classes)
        self.assertIn('asset-provider-youtube', css_classes)
        self.assertIn('asset-%s' % asset.asset_id, css_classes)


class LocalImageAssetModelTest(FileCleanupMixin, TestCase):
    def test_get_thumbnail_url_indexed_png(self):
        """
        Test that get_thumbnail_url works when an indexed PNG is
        used for the image.

        See #726
        """
        asset_type = 'image'
        asset_title = "Test Image Asset"
        asset_caption = "This is a test image"
        image_filename = "test_image-indexed.png"

        app_dir = os.path.dirname(os.path.abspath(__file__))
        img_path = os.path.join(app_dir, "test_files", image_filename)
        with open(img_path) as image:
            asset = create_local_image_asset(
                type=asset_type,
                image=image,
                image_filename=image_filename,
                title=asset_title,
                caption=asset_caption)
            self.add_file_to_cleanup(asset.image.file.path)
            url = asset.get_thumbnail_url(width=222, height=222)
            self.assertIn(image_filename, url)


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

    def test_string_representation_from_body_truncated(self):
        """
        Test that string representations made from the body are truncated
        to 100 characters
        """
        asset = create_html_asset(type='text', title="", caption="", body='<script type="text/javascript" src="//ajax.googleapis.com/ajax/static/modules/gviz/1.0/chart.js">{"dataSourceUrl":"//docs.google.com/spreadsheet/tq?key=0AhWnhIC_xoBpdEpNQkRpdGN6V1FJQ1Y4NEVhQU83b1E&transpose=0&headers=1&range=R12%3AV20&gid=0&pub=1","options":{"vAxes":[{"title":"Cost in Dollars","useFormatFromData":true,"viewWindowMode":"pretty","gridlines":{"count":"10"},"viewWindow":{}},{"useFormatFromData":true,"viewWindowMode":"pretty","viewWindow":{}}],"title":"Cost Per Nutrients","booleanRole":"certainty","animation":{"duration":0},"hAxis":{"title":"\\"Food\\" Name","useFormatFromData":true,"viewWindowMode":"pretty","viewWindow":{}},"isStacked":false,"width":600,"height":371},"state":{},"chartType":"ColumnChart","chartName":"Chart 4"}</script>\n', status='published')
        self.assertEqual(len(asset.__unicode__()), 100)

    def test_get_thumbnail_url(self):
        asset = create_html_asset(type='text', title="", caption="", body='<a title="SAM_1367 by JDenzler, on Flickr" href="http://www.flickr.com/photos/79208145@N08/7803936842/"><img src="http://farm8.staticflickr.com/7261/7803936842_19ec7bf391_n.jpg" alt="SAM_1367" width="320" height="240" /></a>', status='published')
        self.assertEqual(asset.get_thumbnail_url(),
            "http://farm8.staticflickr.com/7261/7803936842_19ec7bf391_n.jpg")

    def test_strings(self):
        """
        Test that the strings method of the model returns the body field
        """
        body = """"As Tina Griego writes for the Children's Corridor website, waves of immigration and a steep rise in births to foreign-born are both a challenge and an opportunity for communities living in the Children's Corridor: "With...immigration came many people with little formal education. The less education one has, the higher the risk of living in poverty."

Data from the Pew Hispanic Center, which Griego cites in her article, shows that 60 percent of immigrants ages 25 and over have less than a high school education. These national statistics are reflected in here in Colorado through birth data. This graphic uses data from birth certificates to look at the education discrepancies between mothers born in the United States and mothers immigrating from a foreign country.

In 2010, there were 66,346 births in Colorado. Of those births, 99.8% of mothers reported their country of origin on the birth certificate. Nearly four-firths of births were to mothers born in the U.S. A fifth of mothers immigrated here from another country. Of those mothers, more than half came from Mexico. The difference in education level among these groups is striking: 12 percent of U.S.-born mothers had less than a high school education, compared to 69 percent of mothers from Mexico and 16 percent of mothers from other countries."""
        asset = create_html_asset(type='text', title="", caption="",
                                  body=body, status='published')
        self.assertEqual(asset.strings(), body)

    def test_strings_strip_html(self):
        """
        Test that the strings method of the model returns the value of
        the body field, but strips HTML from it.
        """
        body = """As
<a rel="nofollow" target="_blank" href="http://www.denverchildrenscorridor.org/data/why-the-battle-against-childhood-poverty-must-include-immigrant-integration">Tina Griego writes for the Children's Corridor website</a>
, waves of immigration and a steep rise in births to foreign-born are both a challenge and an opportunity for communities living in the Children's Corridor: "With...immigration came many people with little formal education. The less education one has, the higher the risk of living in poverty."
<br>"""
        asset = create_html_asset(type='text', title="", caption="",
                                  body=body, status='published')
        self.assertEqual(asset.strings(), striptags(body))

    def test_has_script_google_charts(self):
        body = "<script GOOGLE EMBED CODE GOES HERE> ... </script>"
        asset = create_html_asset(type='chart', title="", caption="", body=body)
        self.assertTrue(asset.has_script())

    def test_has_script_google_charts_capitalized(self):
        body = "<SCRIPT GOOGLE EMBED CODE GOES HERE> ... </script>"
        asset = create_html_asset(type='chart', title="", caption="", body=body)
        self.assertTrue(asset.has_script())

    def test_has_script_fakeout(self):
        body = "<p>This is a string with the word script in it</p>"
        asset = create_html_asset(type='chart', title="", caption="", body=body)
        self.assertFalse(asset.has_script())


class MockProviderTest(TestCase):
    def test_get_google_spreadsheet_embed(self):
        url = 'https://docs.google.com/spreadsheet/pub?key=0As2exFJJWyJqdDhBejVfN1RhdDg2b0QtYWR4X2FTZ3c&output=html' 
        expected = "<iframe width='500' height='300' frameborder='0' src='%s&widget=true'></iframe>" % url
        provider = GoogleSpreadsheetProvider()
        response = provider.request(url)
        self.assertEqual(response['html'], expected)


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
    def filter_dict(self, seq, key, value):
        def has_matching_value(item):
            v = item.get(key, None)
            if v and v == value:
                return True
            else:
                return False

        return list(ifilter(has_matching_value, seq))

    def setUp(self):
        super(DataSetResourceTest, self).setUp()
        self.api_client = TestApiClient()
        self.username = 'test'
        self.password = 'test'
        self.user = User.objects.create_user(self.username, 
            'test@example.com', self.password)
        self.user2 = User.objects.create_user("test2", "test2@example.com",
                                              "test2")
        self.story = create_story(title="Test Story", summary="Test Summary",
            byline="Test Byline", status="published", language="en", 
            author=self.user)
        self.asset = create_html_asset(type='chart',
                title="", caption="",
                body="This would be an embed code",
                status='published',
                owner=self.user)
        self.dataset_attrs = [
            {
                'title': "Metro Denver Free and Reduced Lunch Trends by School District",
                'url': 'http://www.box.com/s/erutk9kacq6akzlvqcdr',
                'source': "Colorado Department of Education",
                'attribution': "The Piton Foundation",
                'links_to_file': False,
                'owner': self.user,
                'status': 'published',
            },
            {
                'title': "Chicago Street Names",
                'description': "List of all Chicago streets with suffixes and minimum and maximum address numbers.",
                'url': 'https://data.cityofchicago.org/Transportation/Chicago-Street-Names/i6bp-fvbx',
                'links_to_file': False,
                'owner': self.user,
                'status': 'published',
            },
            {
                'title': "Illinois Neighborhood Boundaries",
                'description': "Illinois Neighborhood shapes available below, zipped up in the Arc Shapefile format.",
                'url': 'http://www.zillow.com/static/shp/ZillowNeighborhoods-IL.zip',
                'links_to_file': True,
                'source': "Zillow",
                'owner': self.user,
                'status': 'published',
            },
        ]
        self.datasets = []

    def test_get_list(self):
        """
        Test that a user can get a list of datasets
        """
        for dataset_attr in self.dataset_attrs:
            self.datasets.append(create_external_dataset(**dataset_attr))
        self.story.datasets.add(self.datasets[0], self.datasets[1])
        self.story.save()
        self.assertEqual(len(self.story.datasets.all()), 2)
        uri = '/api/0.1/datasets/stories/%s/' % (self.story.story_id)
        resp = self.api_client.get(uri)
        self.assertValidJSONResponse(resp)
        self.assertEqual(len(self.deserialize(resp)['objects']), 2)
        for resp_obj in self.deserialize(resp)['objects']:
            attrs = self.filter_dict(self.dataset_attrs, 'title',
                                     resp_obj['title'])[0]
            for key, value in attrs.items():
                if key != 'owner':
                    self.assertEqual(resp_obj[key], value)

    def test_get_list_published_only(self):
        """
        Test that an unauthenticated user only sees published datasets
        """
        self.dataset_attrs[2]['status'] = 'draft'
        for dataset_attr in self.dataset_attrs:
            self.datasets.append(create_external_dataset(**dataset_attr))
        self.story.datasets.add(*self.datasets)
        self.story.save()
        uri = '/api/0.1/datasets/stories/%s/' % (self.story.story_id)
        resp = self.api_client.get(uri)
        self.assertValidJSONResponse(resp)
        self.assertEqual(len(self.deserialize(resp)['objects']), 2)
        for resp_obj in self.deserialize(resp)['objects']:
            attrs = self.filter_dict(self.dataset_attrs, 'title',
                                     resp_obj['title'])[0]
            for key, value in attrs.items():
                if key != 'owner':
                    self.assertEqual(resp_obj[key], value)
        self.assertEqual(len(self.filter_dict(
            self.deserialize(resp)['objects'],
            'title', "Illinois Neighborhood Boundaries")), 0)

    def test_get_list_own(self):
        """
        Test that a user can get a list of  both published and 
        unpublished datasets that they own
        """
        self.dataset_attrs[0]['status'] = 'draft'
        self.dataset_attrs[2]['status'] = 'draft'
        self.dataset_attrs[2]['owner'] = self.user2 
        for dataset_attr in self.dataset_attrs:
            self.datasets.append(create_external_dataset(**dataset_attr))
        self.story.datasets.add(self.datasets[0], self.datasets[1])
        self.story.save()
        self.api_client.client.login(username=self.username,
                                     password=self.password)
        uri = '/api/0.1/datasets/stories/%s/' % (self.story.story_id)
        resp = self.api_client.get(uri)
        self.assertValidJSONResponse(resp)
        self.assertEqual(len(self.deserialize(resp)['objects']), 2)
        for resp_obj in self.deserialize(resp)['objects']:
            attrs = self.filter_dict(self.dataset_attrs, 'title',
                                     resp_obj['title'])[0]
            for key, value in attrs.items():
                if key != 'owner':
                    self.assertEqual(resp_obj[key], value)
        self.assertEqual(len(self.filter_dict(
            self.deserialize(resp)['objects'],
            'title', "Illinois Neighborhood Boundaries")), 0)

    def test_post_list_url(self):
        post_data = {
            'title': "Chicago Street Names",
            'description': "List of all Chicago streets with suffixes and minimum and maximum address numbers.",
            'url': 'https://data.cityofchicago.org/Transportation/Chicago-Street-Names/i6bp-fvbx',
            'links_to_file': False,
            'language': "en",
        }
        self.assertEqual(DataSet.objects.count(), 0)
        self.api_client.client.login(username=self.username,
                                     password=self.password)
        uri = '/api/0.1/datasets/'
        resp = self.api_client.post(uri, format='json', data=post_data)
        self.assertHttpCreated(resp)
        returned_id = resp['location'].split('/')[-2]
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
        created_dataset = DataSet.objects.get_subclass()
        # Compare the id from the resource URI with the created dataset
        self.assertEqual(created_dataset.dataset_id, returned_id)
        # Compare the created model instance with the post data
        self.assertEqual(created_dataset.title, post_data['title'])
        self.assertEqual(created_dataset.description, post_data['description'])
        self.assertEqual(created_dataset.url, post_data['url'])
        self.assertEqual(created_dataset.links_to_file, post_data['links_to_file'])
        # Test that the owner of the dataset is our logged-in user
        self.assertEqual(created_dataset.owner, self.user)
        # Test that the created dataset is associated with a story 

    def test_post_list_with_story_file_as_data_url(self):
        """
        Test that a user can create a resource including uploading a file
        """
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
        uri = '/api/0.1/datasets/stories/%s/' % (self.story.story_id)
        resp = self.api_client.post(uri, format='json', data=post_data)
        self.assertHttpCreated(resp)
        returned_id = resp['location'].split('/')[-2]
        self.assertEqual(DataSet.objects.count(), 1)
        # Compare the response data with the post data
        self.assertEqual(self.deserialize(resp)['title'], 
                         post_data['title'])
        self.assertEqual(self.deserialize(resp)['description'], 
                         post_data['description'])
        created_dataset = DataSet.objects.get_subclass()
        # Compare the id from the resource URI with the created dataset
        self.assertEqual(created_dataset.dataset_id, returned_id)
        # Compare the created model instance with the post data
        self.assertEqual(created_dataset.title, post_data['title'])
        self.assertEqual(created_dataset.description, post_data['description'])
        # Compare the uploaded file and the original 
        created_hash = hashlib.sha1(
            file(created_dataset.file.path, 'r').read()).digest()
        self.assertEqual(original_hash, created_hash)
        # Set our created file to be cleaned up
        self.add_file_to_cleanup(created_dataset.file.file.path)
        # Test that the owner of the dataset is our logged-in user
        self.assertEqual(created_dataset.owner, self.user)
        # Test that the created dataset is associated with a story 
        self.assertIn(self.story, created_dataset.stories.all())

    def test_post_list_with_story_file_as_multipart(self):
        """Test that a user can create a new dataset with a file sent as multipart form data"""  
        data_filename = "test_data.csv"
        app_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(app_dir, "test_files", data_filename)
        original_hash = hashlib.sha1(file(data_path, 'r').read()).digest()
        uri = '/api/0.1/datasets/stories/%s/' % (self.story.story_id)
        with open(data_path) as fp:
            post_data = {
                'title': "Test Dataset",
                'description': "A test dataset",
                'language': "en",
                'file': fp, 
            }
            self.assertEqual(DataSet.objects.count(), 0)
            self.api_client.client.login(username=self.username,
                                         password=self.password)
            resp = self.api_client.client.post(uri,
                data=post_data)
            self.assertHttpCreated(resp)
            returned_id = resp['location'].split('/')[-2]
            self.assertEqual(DataSet.objects.count(), 1)
            # Compare the response data with the post data
            self.assertEqual(self.deserialize(resp)['title'], 
                             post_data['title'])
            self.assertEqual(self.deserialize(resp)['description'], 
                             post_data['description'])
            created_dataset = DataSet.objects.get_subclass()
            # Compare the id from the resource URI with the created dataset
            self.assertEqual(created_dataset.dataset_id, returned_id)
            # Compare the created model instance with the post data
            self.assertEqual(created_dataset.title, post_data['title'])
            self.assertEqual(created_dataset.description, post_data['description'])
            # Compare the uploaded file and the original 
            created_hash = hashlib.sha1(
                file(created_dataset.file.path, 'r').read()).digest()
            self.assertEqual(original_hash, created_hash)
            # Set our created file to be cleaned up
            self.add_file_to_cleanup(created_dataset.file.file.path)
            # Test that the owner of the dataset is our logged-in user
            self.assertEqual(created_dataset.owner, self.user)
            # Test that the created dataset is associated with a story 
            self.assertIn(self.story, created_dataset.stories.all())

    def test_post_list_with_story_no_file_or_url(self):
        """
        Test that a user receives an error when trying to create a dataset without
        specifying a file or URL
        """
        post_data = {
            'title': "Test Dataset",
            'description': "A test dataset",
            'language': "en",
        }
        self.assertEqual(DataSet.objects.count(), 0)
        self.api_client.client.login(username=self.username,
                                     password=self.password)
        uri = '/api/0.1/datasets/stories/%s/' % (self.story.story_id)
        resp = self.api_client.post(uri, format='json', data=post_data)
        self.assertHttpBadRequest(resp)
        self.assertEqual(DataSet.objects.count(), 0)

    def test_post_list_with_story_url(self):
        post_data = {
            'title': "Chicago Street Names",
            'description': "List of all Chicago streets with suffixes and minimum and maximum address numbers.",
            'url': 'https://data.cityofchicago.org/Transportation/Chicago-Street-Names/i6bp-fvbx',
            'links_to_file': False,
            'language': "en",
        }
        self.assertEqual(DataSet.objects.count(), 0)
        self.api_client.client.login(username=self.username,
                                     password=self.password)
        uri = '/api/0.1/datasets/stories/%s/' % (self.story.story_id)
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
        # Test that the owner of the dataset is our logged-in user
        self.assertEqual(created_dataset.owner, self.user)
        # Test that the created dataset is associated with a story 
        self.assertIn(self.story, created_dataset.stories.all())

    def test_post_list_with_story_unauthenticated(self):
        """Test that an unauthenticated user can't create a dataset"""
        post_data = {
            'title': "Test Dataset",
            'description': "A test dataset",
            'url': 'https://data.cityofchicago.org/Transportation/Chicago-Street-Names/i6bp-fvbx',
            'links_to_file': False,
            'language': "en",
        }
        self.assertEqual(DataSet.objects.count(), 0)
        uri = '/api/0.1/datasets/stories/%s/' % (self.story.story_id)
        resp = self.api_client.post(uri, format='json', data=post_data)
        self.assertHttpUnauthorized(resp)
        self.assertEqual(DataSet.objects.count(), 0)

    def test_post_list_with_story_unauthorized(self):
        """
        Test that a user can't create a dataset associated with another
        user's story
        """
        post_data = {
            'title': "Test Dataset",
            'description': "A test dataset",
            'url': 'https://data.cityofchicago.org/Transportation/Chicago-Street-Names/i6bp-fvbx',
            'links_to_file': False,
            'language': "en",
        }
        self.story.author = self.user2
        self.story.save()
        self.assertEqual(DataSet.objects.count(), 0)
        self.api_client.client.login(username=self.username,
                                     password=self.password)
        uri = '/api/0.1/datasets/stories/%s/' % (self.story.story_id)
        resp = self.api_client.post(uri, format='json', data=post_data)
        self.assertHttpUnauthorized(resp)
        self.assertEqual(DataSet.objects.count(), 0)

    def test_post_list_with_story_nonexistant_story(self):
        """Test that dataset creation fails when a story matching
        the specified story_id doesn't exist"""
        post_data = {
            'title': "Test Dataset",
            'description': "A test dataset",
            'url': 'https://data.cityofchicago.org/Transportation/Chicago-Street-Names/i6bp-fvbx',
            'links_to_file': False,
            'language': "en",
        }
        nonexistant_story_id = '15844bc0d5c911e19b230800200c9a66'
        self.assertEqual(DataSet.objects.count(), 0)
        self.api_client.client.login(username=self.username,
                                     password=self.password)
        uri = '/api/0.1/datasets/stories/%s/' % (nonexistant_story_id)
        resp = self.api_client.post(uri, format='json', data=post_data)
        self.assertHttpNotFound(resp)
        self.assertEqual(DataSet.objects.count(), 0)

    def test_post_list_with_asset_url(self):
        post_data = {
            'title': "Chicago Street Names",
            'description': "List of all Chicago streets with suffixes and minimum and maximum address numbers.",
            'url': 'https://data.cityofchicago.org/Transportation/Chicago-Street-Names/i6bp-fvbx',
            'links_to_file': False,
            'language': "en",
        }
        self.assertEqual(DataSet.objects.count(), 0)
        self.api_client.client.login(username=self.username,
                                     password=self.password)
        uri = '/api/0.1/datasets/assets/%s/' % (self.asset.asset_id)
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
        # Test that the owner of the dataset is our logged-in user
        self.assertEqual(created_dataset.owner, self.user)
        # Test that the created dataset is associated with a story 
        self.assertIn(self.asset, created_dataset.assets.select_subclasses())

    def test_get_list_for_asset(self):
        """
        Test that a user can get a list of datasets associated with an asset
        """
        for dataset_attr in self.dataset_attrs:
            self.datasets.append(create_external_dataset(**dataset_attr))
        self.asset.datasets.add(self.datasets[0], self.datasets[1])
        self.asset.save()
        self.assertEqual(len(self.asset.datasets.all()), 2)
        uri = '/api/0.1/datasets/assets/%s/' % (self.asset.asset_id)
        resp = self.api_client.get(uri)
        self.assertValidJSONResponse(resp)
        self.assertEqual(len(self.deserialize(resp)['objects']), 2)
        for resp_obj in self.deserialize(resp)['objects']:
            attrs = self.filter_dict(self.dataset_attrs, 'title',
                                     resp_obj['title'])[0]
            for key, value in attrs.items():
                if key != 'owner':
                    self.assertEqual(resp_obj[key], value)

    def test_post_list_with_asset_unauthorized(self):
        """
        Test that a user can't create a dataset associated with another
        user's asset 
        """
        post_data = {
            'title': "Test Dataset",
            'description': "A test dataset",
            'url': 'https://data.cityofchicago.org/Transportation/Chicago-Street-Names/i6bp-fvbx',
            'links_to_file': False,
            'language': "en",
        }
        self.asset.owner = self.user2
        self.asset.save()
        self.assertEqual(DataSet.objects.count(), 0)
        self.api_client.client.login(username=self.username,
                                     password=self.password)
        uri = '/api/0.1/datasets/assets/%s/' % (self.asset.asset_id)
        resp = self.api_client.post(uri, format='json', data=post_data)
        self.assertHttpUnauthorized(resp)
        self.assertEqual(DataSet.objects.count(), 0)

    def test_post_list_with_asset_nonexistant_asset(self):
        """Test that dataset creation fails when a asset matching
        the specified asset_id doesn't exist"""
        post_data = {
            'title': "Test Dataset",
            'description': "A test dataset",
            'url': 'https://data.cityofchicago.org/Transportation/Chicago-Street-Names/i6bp-fvbx',
            'links_to_file': False,
            'language': "en",
        }
        nonexistant_asset_id = '15844bc0d5c911e19b230800200c9a66'
        self.assertEqual(DataSet.objects.count(), 0)
        self.api_client.client.login(username=self.username,
                                     password=self.password)
        uri = '/api/0.1/datasets/assets/%s/' % (nonexistant_asset_id)
        resp = self.api_client.post(uri, format='json', data=post_data)
        self.assertHttpNotFound(resp)
        self.assertEqual(DataSet.objects.count(), 0)

    def test_delete_detail_for_asset(self):
        """
        Test that a user can disassociate a datasets from an asset
        """
        for dataset_attr in self.dataset_attrs:
            self.datasets.append(create_external_dataset(**dataset_attr))
        self.asset.datasets.add(self.datasets[0], self.datasets[1])
        self.asset.save()
        self.assertEqual(len(self.asset.datasets.all()), 2)
        disassociate_dataset = self.datasets[0]
        self.api_client.client.login(username=self.username,
                                     password=self.password)
        uri = '/api/0.1/datasets/assets/%s/%s/' % (self.asset.asset_id,
                disassociate_dataset.dataset_id)
        resp = self.api_client.delete(uri)
        self.assertHttpAccepted(resp)
        try:
            # Test that we didn't delete the dataset
            dataset = DataSet.objects.get(
                    dataset_id=disassociate_dataset.dataset_id)
            self.assertNotEqual(dataset.status, 'deleted') 
            # Refresh the asset
            asset = Asset.objects.get_subclass(asset_id=self.asset.asset_id)
            # Check that the dataset is no longer associated
            self.assertNotIn(disassociate_dataset, asset.datasets.all())
            # Check that we didn't accidently clobber other
            # datasets associated with the asset
            self.assertEqual(asset.datasets.all().count(), 1)
            self.assertIn(self.datasets[1], asset.datasets.select_subclasses())
        except DataSet.DoesNotExist:
            self.fail("Data set was removed, it should only have been disassociated")

    def test_delete_detail_for_asset_unauthorized(self):
        """
        Test that a user cannot disassociate datasets from another user's asset
        """
        for dataset_attr in self.dataset_attrs:
            self.datasets.append(create_external_dataset(**dataset_attr))
        self.asset.datasets.add(self.datasets[0], self.datasets[1])
        self.asset.owner = self.user2
        self.asset.save()
        self.assertEqual(len(self.asset.datasets.all()), 2)
        disassociate_dataset = self.datasets[0]
        self.api_client.client.login(username=self.username,
                                     password=self.password)
        uri = '/api/0.1/datasets/assets/%s/%s/' % (self.asset.asset_id,
                disassociate_dataset.dataset_id)
        resp = self.api_client.delete(uri)
        self.assertHttpUnauthorized(resp)
        self.assertEqual(len(self.asset.datasets.all()), 2)

    def test_delete_detail_for_asset_not_found(self):
        """
        Test that a user cannot disassociate datasets from another user's asset
        """
        for dataset_attr in self.dataset_attrs:
            self.datasets.append(create_external_dataset(**dataset_attr))
        self.asset.datasets.add(self.datasets[0], self.datasets[1])
        self.asset.owner = self.user2
        self.asset.save()
        self.assertEqual(len(self.asset.datasets.all()), 2)
        self.api_client.client.login(username=self.username,
                                     password=self.password)
        uri = '/api/0.1/datasets/assets/%s/%s/' % (self.asset.asset_id,
                'this-is-not-a-uuid')
        resp = self.api_client.delete(uri)
        self.assertHttpNotFound(resp)
        self.assertEqual(len(self.asset.datasets.all()), 2)

    def test_non_delete_detail_for_assets(self):
        """
        Test that methods other than delete aren't supported for the asset
        detail
        """
        for dataset_attr in self.dataset_attrs:
            self.datasets.append(create_external_dataset(**dataset_attr))
        self.asset.datasets.add(self.datasets[0], self.datasets[1])
        self.asset.save()
        self.assertEqual(len(self.asset.datasets.all()), 2)
        disassociate_dataset = self.datasets[0]
        self.api_client.client.login(username=self.username,
                                     password=self.password)
        uri = '/api/0.1/datasets/assets/%s/%s/' % (self.asset.asset_id,
                disassociate_dataset.dataset_id)
        resp = self.api_client.get(uri)
        self.assertHttpMethodNotAllowed(resp)
        resp = self.api_client.post(uri, format='json', data={})
        self.assertHttpMethodNotAllowed(resp)
        resp = self.api_client.put(uri, format='json', data={})
        self.assertHttpMethodNotAllowed(resp)

    def test_delete_detail_file(self):
        """
        Test that a user can delete a dataset with an associated file 
        """
        data_filename = "test_data.csv"
        app_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(app_dir, "test_files", data_filename)
        encoded_file = self.read_as_data_url(data_path)

        post_data = {
            'title': "Test Dataset",
            'description': "A test dataset",
            'file': encoded_file,
            'filename': data_filename,
            'language': "en",
        }
        self.api_client.client.login(username=self.username,
                                     password=self.password)
        uri = '/api/0.1/datasets/stories/%s/' % (self.story.story_id)
        resp = self.api_client.post(uri, format='json', data=post_data)
        self.assertHttpCreated(resp)
        self.assertEqual(DataSet.objects.count(), 1)
        created_dataset = DataSet.objects.get_subclass()
        file_path = created_dataset.file.path
        resource_uri = self.deserialize(resp)['resource_uri']
        resp = self.api_client.delete(resource_uri, format='json')
        self.assertHttpAccepted(resp)
        self.assertEqual(DataSet.objects.count(), 0)
        self.assertFalse(os.path.exists(file_path))

    def test_delete_detail_url(self):
        post_data = {
            'title': "Chicago Street Names",
            'description': "List of all Chicago streets with suffixes and minimum and maximum address numbers.",
            'url': 'https://data.cityofchicago.org/Transportation/Chicago-Street-Names/i6bp-fvbx',
            'links_to_file': False,
            'language': "en",
        }
        self.assertEqual(DataSet.objects.count(), 0)
        self.api_client.client.login(username=self.username,
                                     password=self.password)
        uri = '/api/0.1/datasets/stories/%s/' % (self.story.story_id)
        resp = self.api_client.post(uri, format='json', data=post_data)
        self.assertHttpCreated(resp)
        self.assertEqual(DataSet.objects.count(), 1)
        resource_uri = self.deserialize(resp)['resource_uri']
        resp = self.api_client.delete(resource_uri, format='json')
        self.assertHttpAccepted(resp)
        self.assertEqual(DataSet.objects.count(), 0)

    def test_delete_detail_unauthenticated(self):
        """Test that an unauthenticated user can't delete a dataset"""
        dataset = create_external_dataset(**self.dataset_attrs[0])
        self.assertEqual(DataSet.objects.count(), 1)
        uri = '/api/0.1/datasets/%s/' % (dataset.dataset_id)
        resp = self.api_client.delete(uri, format='json')
        self.assertHttpUnauthorized(resp)
        self.assertEqual(DataSet.objects.count(), 1)

    def test_delete_detail_unauthorized(self):
        self.dataset_attrs[0]['owner'] = self.user2
        dataset = create_external_dataset(**self.dataset_attrs[0])
        self.assertEqual(DataSet.objects.count(), 1)
        uri = '/api/0.1/datasets/%s/' % (dataset.dataset_id)
        self.api_client.client.login(username=self.username,
                                     password=self.password)
        resp = self.api_client.delete(uri, format='json')
        self.assertHttpUnauthorized(resp)
        self.assertEqual(DataSet.objects.count(), 1)

    def _assert_put_unauthorized(self, resp, dataset, put_data):
        self.assertHttpUnauthorized(resp)
        dataset = DataSet.objects.get_subclass(pk=dataset.pk)
        self.assertNotEqual(dataset.title, put_data['title'])
        self.assertNotEqual(dataset.url, put_data['url'])

    def test_put_detail_unauthenticated(self):
        """Test that an unauthenticated user can't update a dataset"""
        put_data = {
            'title': "Chicago Street Names",
            'description': "List of all Chicago streets with suffixes and minimum and maximum address numbers.",
            'url': 'https://data.cityofchicago.org/Transportation/Chicago-Street-Names/i6bp-fvbx',
            'links_to_file': False,
            'language': "en",
        }
        dataset = create_external_dataset(**self.dataset_attrs[0])
        self.assertEqual(DataSet.objects.count(), 1)
        uri = '/api/0.1/datasets/%s/' % (dataset.dataset_id)
        resp = self.api_client.put(uri, format='json', data=put_data)
        self._assert_put_unauthorized(resp, dataset, put_data)

    def test_put_detail_unauthorized(self):
        put_data = {
            'title': "Chicago Street Names",
            'description': "List of all Chicago streets with suffixes and minimum and maximum address numbers.",
            'url': 'https://data.cityofchicago.org/Transportation/Chicago-Street-Names/i6bp-fvbx',
            'links_to_file': False,
            'language': "en",
        }
        self.dataset_attrs[0]['owner'] = self.user2
        dataset = create_external_dataset(**self.dataset_attrs[0])
        self.assertEqual(DataSet.objects.count(), 1)
        uri = '/api/0.1/datasets/%s/' % (dataset.dataset_id)
        self.api_client.client.login(username=self.username,
                                     password=self.password)
        resp = self.api_client.put(uri, format='json', data=put_data)
        self._assert_put_unauthorized(resp, dataset, put_data)

    def test_put_detail_url(self):
        dataset = create_external_dataset(**self.dataset_attrs[0])
        self.assertEqual(DataSet.objects.count(), 1)
        uri = '/api/0.1/datasets/%s/' % (dataset.dataset_id)
        self.api_client.client.login(username=self.username,
                                     password=self.password)
        resp = self.api_client.get(uri, format='json')
        put_data = self.deserialize(resp)
        put_data['title'] = "New Title"
        put_data['url'] = "http://floodlightproject.org/data.csv"
        resp = self.api_client.put(uri, format='json', data=put_data)
        self.assertHttpAccepted(resp)
        dataset = DataSet.objects.get_subclass(pk=dataset.pk)
        self.assertEqual(dataset.title, put_data['title'])
        self.assertEqual(dataset.url, put_data['url'])

    def get_put_detail_data(self, dataset, data_file):
        """Get PUT data for a given dataset"""
        return {
            'attribution': '',
            'created': dataset.created.isoformat(),
            'dataset_id': dataset.dataset_id,
            'description': dataset.description,
            'download_url': dataset.download_url(), 
            'file': data_file,
            'language': 'en',
            'languages': dataset.get_language_names(),
            'last_edited': dataset.last_edited.isoformat(),
            'links_to_file': dataset.links_to_file,
            'resource_uri': '/api/0.1/datasets/%s/' % (dataset.dataset_id),
            'status': 'draft',
            'title': dataset.title,
        }

    def do_request_detail(self, method='put', content_type=MULTIPART_CONTENT, qs=None):
        """
        Construct a dataset instance, create a payload and make a request
        to the detail endpoint to try to replace the dataset's attributes

        Returns a tuple of the created dataset, the hash of the original
        data file and the response
        """
        data_filename = "test_data.csv"
        replacement_data_filename = "test_data2.csv"
        app_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(app_dir, "test_files", data_filename)
        with open(data_path) as data_file:
            dataset = create_local_dataset(
                data_file=data_file,
                data_filename=data_filename,
                title="Test Image Asset",
                owner=self.user
            )
            self.add_file_to_cleanup(dataset.file.file.path)

        data_path = os.path.join(app_dir, "test_files", replacement_data_filename)
        original_hash = hashlib.sha1(file(data_path, 'r').read()).digest()
        detail_url = '/api/0.1/datasets/%s/' % (dataset.dataset_id)
        if qs is not None:
            detail_url += qs
        with open(data_path) as data_file:
            put_data = self.get_put_detail_data(dataset, data_file) 
            self.api_client.client.login(username=self.username,
                                         password=self.password)
            func = getattr(self.api_client.client, method)
            if method == 'put' and django.VERSION >= (1, 5):
                put_data = encode_multipart(BOUNDARY, put_data)
            resp = func(detail_url, data=put_data, content_type=content_type)
            return (dataset, original_hash, resp)

    def _test_put_detail_success(self, dataset, original_hash, resp):
        """
        Test that a PUT request to a detail endpoint successfully
        updates a dataset's file

        This is a helper to make individual tests more DRY
        """
        self.assertHttpAccepted(resp)
        self.assertEqual(DataSet.objects.count(), 1)
        # Refresh the dataset
        dataset = DataSet.objects.get_subclass(dataset_id=dataset.dataset_id)
        # Set our created file to be cleaned up
        self.add_file_to_cleanup(dataset.file.file.path)
        # Compare the uploaded file and the original 
        created_hash = hashlib.sha1(file(dataset.file.path, 'r').read()).digest()
        self.assertEqual(original_hash, created_hash)

    def test_put_detail_file_as_multipart(self):
        (dataset, original_hash, resp) = self.do_request_detail()
        self._test_put_detail_success(dataset, original_hash, resp)

    def test_post_detail_file_as_multipart_non_iframe(self):
        """
        Test that a POST to the detail endpoint fails without the
        ``iframe`` querystring parameter.
        """
        (dataset, original_hash, resp) = self.do_request_detail(method='post')
        self.assertHttpNotImplemented(resp)
        self.assertEqual(DataSet.objects.count(), 1)
        # Refresh the dataset
        dataset = DataSet.objects.get_subclass(dataset_id=dataset.dataset_id)
        # Compare the uploaded file and the original 
        created_hash = hashlib.sha1(file(dataset.file.path, 'r').read()).digest()
        self.assertNotEqual(original_hash, created_hash)

    def test_post_detail_file_as_multipart_iframe(self):
        """
        Test that a POST to the detail endpoint works the same as a
        PUT when the ``iframe`` querystring parameter is present.
        """
        (dataset, original_hash, resp) = self.do_request_detail(method='post',
                qs="?iframe=iframe")
        self._test_put_detail_success(dataset, original_hash, resp)


class ExternalDataSetModelTest(TestCase):
    def test_url_is_for_file(self):
        self.assertFalse(ExternalDataSet.url_is_for_file('http://www.box.com/s/erutk9kacq6akzlvqcdr'))
        self.assertTrue(ExternalDataSet.url_is_for_file("http://floodlightproject.org/data.csv"))

    def test_set_links_to_file(self):
        """
        Test that ``links_to_file`` attribute is properly set when a 
        DataSet is created
        """
        dataset = create_external_dataset(title="Test DataSet", url="http://www.box.com/s/erutk9kacq6akzlvqcdr")
        self.assertFalse(dataset.links_to_file)
        dataset = create_external_dataset(title="Test DataSet", url="http://floodlightproject.org/data.csv")
        self.assertTrue(dataset.links_to_file)


class DataSetApiTest(TestCase):
    """ Test the public API for creating DataSets """

    def test_create_external_dataset(self):
        """Test create_external_dataset()"""
        user = User.objects.create(username='admin')
        url = 'http://www.box.com/s/erutk9kacq6akzlvqcdr'
        title = ("Metro Denver Free and Reduced Lunch Trends by School "
                 "District")
        source = "Colorado Department of Education"
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

    def test_post_list_image_as_multipart(self):
        """Test creating a new image asset with the image sent as multipart form data"""
        image_filename = "test_image.jpg"

        app_dir = os.path.dirname(os.path.abspath(__file__))
        img_path = os.path.join(app_dir, "test_files", image_filename)
        original_hash = hashlib.sha1(file(img_path, 'r').read()).digest()
        with open(img_path) as image:
            post_data = {
                'type': "image",
                'title': "Test Image Asset",
                'caption': "This is a test image",
                'status': "published",
                'filename': image_filename,
                'image': image,
                'language': "en",
            }
            self.assertEqual(Asset.objects.count(), 0)
            self.api_client.client.login(username=self.username,
                                         password=self.password)
            resp = self.api_client.client.post('/api/0.1/assets/',
                                               data=post_data)
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

    def test_post_list_unsupported_image(self):
        """Test that an error is returned creating a new image asset when the image file is an unsupported format"""
        image_filename = "test_image.pdf"

        app_dir = os.path.dirname(os.path.abspath(__file__))
        img_path = os.path.join(app_dir, "test_files", image_filename)
        with open(img_path) as image:
            post_data = {
                'type': "image",
                'title': "Test Image Asset",
                'caption': "This is a test image",
                'status': "published",
                'filename': image_filename,
                'image': image,
                'language': "en",
            }
            self.assertEqual(Asset.objects.count(), 0)
            self.api_client.client.login(username=self.username,
                                         password=self.password)
            resp = self.api_client.client.post('/api/0.1/assets/',
                                               data=post_data)
            # Check that the endpoint returns an error
            self.assertHttpBadRequest(resp)
            # Check that no asset was created 
            self.assertEqual(Asset.objects.count(), 0)

    def test_post_list_image_as_data_url(self):
        """Test creating an asset with the data stored in an uploaded image encoded as a data URL"""
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

    def test_post_list_image_no_file_or_url(self):
        """
        Test that an error is returned when trying to create an image asset 
        without specifying a file or URL
        
        """
        post_data = {
            'type': "image",
            'title': "Test Image Asset",
            'caption': "This is a test image",
            'status': "published",
            'language': "en",
        }
        self.assertEqual(Asset.objects.count(), 0)
        self.api_client.client.login(username=self.username,
                                     password=self.password)
        resp = self.api_client.post('/api/0.1/assets/',
                               format='json', data=post_data)
        self.assertHttpBadRequest(resp)
        self.assertEqual(Asset.objects.count(), 0)

    def test_post_list_map_no_file_body_or_url(self):
        """
        Test that a map cannot be created when no file, body or url field is
        provided
        """
        post_data = {
            'type': "map",
            'title': "Test Map Asset",
            'status': "published",
            'language': "en",
        }
        self.assertEqual(Asset.objects.count(), 0)
        self.api_client.client.login(username=self.username,
                                     password=self.password)
        resp = self.api_client.post('/api/0.1/assets/',
                               format='json', data=post_data)
        self.assertHttpBadRequest(resp)
        self.assertEqual(Asset.objects.count(), 0)

    def test_put_detail_image_relative_url(self):
        """
        Test that the image field is ignored if it is just put back
        to the endpoint.
        """
        image_filename = "test_image.jpg"
        app_dir = os.path.dirname(os.path.abspath(__file__))
        img_path = os.path.join(app_dir, "test_files", image_filename)
        with open(img_path) as fp:
            post_data = {
                'type': "image",
                'title': "Test Image Asset",
                'caption': "This is a test image",
                'status': "published",
                'filename': image_filename,
                'image': fp,
                'language': "en",
            }
            self.assertEqual(Asset.objects.count(), 0)
            self.api_client.client.login(username=self.username,
                                         password=self.password)
            resp = self.api_client.client.post('/api/0.1/assets/',
                                               data=post_data)
            self.assertHttpCreated(resp)
            base_uri = resp['location']
            created_asset = Asset.objects.get_subclass()
            created_image = created_asset.image
            # Set our created file to be cleaned up
            self.add_file_to_cleanup(created_asset.image.file.path)
            resp = self.api_client.get(base_uri)
            self.assertValidJSONResponse(resp)
            post_data = self.deserialize(resp)
            resp = self.api_client.put(base_uri, format='json',
                                       data=post_data)
            self.assertHttpAccepted(resp)
            created_asset = Asset.objects.get_subclass(
                asset_id=self.deserialize(resp)['asset_id'])
            self.assertEqual(created_asset.image, created_image)

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

    def test_post_list_no_content(self):
        """Test that an error is returned when no image, body or url field is specified"""
        post_data = {
            'title' : "Success Express",
            'type': "quotation",
            'attribution': "Ed Brennan, EdNews Colorado",
            'status': 'published',
            'language': "en",
        }
        self.assertEqual(Asset.objects.count(), 0)
        self.api_client.client.login(username=self.username, password=self.password)
        response = self.api_client.post('/api/0.1/assets/',
                               format='json', data=post_data)
        self.assertHttpBadRequest(response)

    def test_post_list_multiple_content(self):
        """Test that an error is returned when more than one of these fields is specified: image, body, url"""
        post_data = {
            'title' : "Success Express",
            'type': "quotation",
            'attribution': "Ed Brennan, EdNews Colorado",
            'body': "Test Body",
            'url': "http://denverchildrenscorridor.org/",
            'status': 'published',
            'language': "en",
        }
        self.assertEqual(Asset.objects.count(), 0)
        self.api_client.client.login(username=self.username, password=self.password)
        response = self.api_client.post('/api/0.1/assets/',
                               format='json', data=post_data)
        self.assertHttpBadRequest(response)

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

    def test_put_detail_html_caption(self):
        """Test updating an asset's caption"""
        asset = create_html_asset(type='table', title='Test Html Asset',
                                   body="<iframe width='500' height='300' frameborder='0' src='https://docs.google.com/spreadsheet/pub?key=0As2exFJJWyJqdDhBejVfN1RhdDg2b0QtYWR4X2FTZ3c&output=html&widget=true'></iframe>",
                                   attribution="Jane Doe", 
                                   status="published",
                                   owner=self.user)
        self.assertEqual(Asset.objects.count(), 1)
        self.assertEqual(asset.caption, '')
        self.api_client.client.login(username=self.username, password=self.password)
        uri = '/api/0.1/assets/%s/' % (asset.asset_id)
        resp = self.api_client.get(uri, format='json')
        self.assertValidJSONResponse(resp)
        # Copy the put data from the response
        put_data = self.deserialize(resp)
        put_data['caption'] = "New Caption"
        resp = self.api_client.put(uri, format='json', data=put_data)
        self.assertHttpAccepted(resp)
        self.assertEqual(self.deserialize(resp)['caption'], put_data['caption'])
        updated_asset = Asset.objects.get(asset_id=asset.asset_id)
        self.assertEqual(updated_asset.caption, put_data['caption'])
        self.assertEqual(Asset.objects.count(), 1)
        self.assertEqual(HtmlAssetTranslation.objects.count(), 1)

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

    def get_put_detail_data(self, asset, image):
        """Get PUT data for a given image asset"""
        return {
            'language': 'en',
            'type': 'image',
            'url': '',
            'image': image,
            'license': 'CC BY',
            'asset_created': '',
            'asset_id': asset.asset_id,
            'attribution': '',
            'body': '',
            'content': asset.render_html(),
            'created': asset.created.isoformat(),
            'display_title': 'test_image.jpg',
            'languages': asset.get_language_names(),
            'last_edited': asset.last_edited.isoformat(),
            'published': '',
            'resource_uri': '/api/0.1/assets/%s/' % (asset.asset_id),
            'section_specific': 'false',
            'source_url': '',
            'status': 'draft',
            'thumbnail_url': asset.get_thumbnail_url(width=222, height=222),
            'title': '',
            'container': '',
        }

    def do_request_detail(self, method='put', content_type=MULTIPART_CONTENT, qs=None):
        """
        Construct an asset instance, create a payload and make a request
        to the detail endpoint to try to replace the asset's attributes

        Returns a tuple of the created asset, the hash of the original
        asset image and the response
        """
        image_filename = "test_image.jpg"
        replacement_image_filename = "test_image_2.png"
        app_dir = os.path.dirname(os.path.abspath(__file__))
        img_path = os.path.join(app_dir, "test_files", image_filename)
        with open(img_path) as image:
            asset = create_local_image_asset(
                type='image',
                image=image,
                image_filename="test_image.jpg",
                title="Test Image Asset",
                owner=self.user
            )
            self.add_file_to_cleanup(asset.image.file.path)

        img_path = os.path.join(app_dir, "test_files", replacement_image_filename)
        original_hash = hashlib.sha1(file(img_path, 'r').read()).digest()
        detail_url = '/api/0.1/assets/%s/' % (asset.asset_id)
        if qs is not None:
            detail_url += qs
        with open(img_path) as image:
            put_data = self.get_put_detail_data(asset, image) 
            self.api_client.client.login(username=self.username,
                                         password=self.password)
            func = getattr(self.api_client.client, method)
            if method == 'put' and django.VERSION >= (1, 5):
                put_data = encode_multipart(BOUNDARY, put_data)
            resp = func(detail_url, data=put_data, content_type=content_type)
            return (asset, original_hash, resp)

    def _test_put_detail_success(self, asset, original_hash, resp):
        """
        Test that a PUT request to a detail endpoint successfully
        updates an image asset's image file

        This is a helper to make individual tests more DRY
        """
        self.assertHttpAccepted(resp)
        self.assertEqual(Asset.objects.count(), 1)
        # Refresh the asset
        asset = Asset.objects.get_subclass(asset_id=asset.asset_id)
        # Set our created file to be cleaned up
        self.add_file_to_cleanup(asset.image.file.path)
        # Compare the uploaded image and the original 
        created_hash = hashlib.sha1(file(asset.image.path, 'r').read()).digest()
        self.assertEqual(original_hash, created_hash)
         
    def test_put_detail_image_as_multipart(self):
        """Test updating an existing image asset with the image sent as multipart form data"""
        (asset, original_hash, resp) = self.do_request_detail()
        self._test_put_detail_success(asset, original_hash, resp)

    def test_post_detail_image_as_multipart_non_iframe(self):
        """
        Test that a POST to the detail endpoint fails without the
        ``iframe`` querystring parameter.
        """
        (asset, original_hash, resp) = self.do_request_detail(method='post')
        self.assertHttpNotImplemented(resp)
        self.assertEqual(Asset.objects.count(), 1)
        # Refresh the asset
        asset = Asset.objects.get_subclass(asset_id=asset.asset_id)
        # Compare the uploaded image and the original 
        created_hash = hashlib.sha1(file(asset.image.path, 'r').read()).digest()
        self.assertNotEqual(original_hash, created_hash)

    def test_post_detail_image_as_multipart_iframe(self):
        """
        Test that a POST to the detail endpoint works the same as a
        PUT when the ``iframe`` querystring parameter is present.
        """
        (asset, original_hash, resp) = self.do_request_detail(method='post',
                qs="?iframe=iframe")
        self._test_put_detail_success(asset, original_hash, resp)

    def test_delete_detail(self):
        asset = create_html_asset(type='text', title='Test Html Asset',
                                   body='<p>Test body</p>',
                                   attribution="Jane Doe", 
                                   status="published",
                                   owner=self.user)
        uri = '/api/0.1/assets/%s/' % (asset.asset_id)
        self.api_client.client.login(username=self.username,
                                     password=self.password)
        resp = self.api_client.delete(uri)
        self.assertHttpAccepted(resp)
        with self.assertRaises(HtmlAsset.DoesNotExist):
            asset = HtmlAsset.objects.get(asset_id=asset.asset_id)


class AssetResourceFeaturedTest(FileCleanupMixin, ResourceTestCase):
    """Test featured asset endpoints of AssetResource"""

    def setUp(self):
        super(AssetResourceFeaturedTest, self).setUp()
        self.api_client = TestApiClient()
        self.username = 'test'
        self.password = 'test'
        self.user = User.objects.create_user(self.username, 
            'test@example.com', self.password)
        self.user2 = User.objects.create_user("test2", "test2@example.com",
                                              "test2")
        self.story = create_story(title="Test Story", summary="Test Summary",
            byline="Test Byline", status="published", language="en", 
            author=self.user)

    def test_get_list(self):
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
                image_filename="test_image.jpg",
                title=asset_title,
                caption=asset_caption,
                status='published')
            self.add_file_to_cleanup(asset.image.file.path)
            asset2 = create_local_image_asset(
                type=asset_type,
                image=image,
                image_filename="test_image.jpg",
                title=asset_title,
                caption=asset_caption,
                status='published')
            self.add_file_to_cleanup(asset2.image.file.path)
            asset3 = create_local_image_asset(
                type=asset_type,
                image=image,
                image_filename="test_image.jpg",
                title=asset_title,
                caption=asset_caption,
                status='published')
            self.add_file_to_cleanup(asset3.image.file.path)
        self.story.assets.add(asset)
        self.story.featured_assets.add(asset2)
        uri = '/api/0.1/assets/stories/%s/featured/' % (self.story.story_id)
        resp = self.api_client.get(uri, format='json')
        self.assertValidJSONResponse(resp)
        self.assertEqual(len(self.deserialize(resp)['objects']), 1)
        self.assertEqual(self.deserialize(resp)['objects'][0]['asset_id'], asset2.asset_id)

    def test_put_list(self):
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
                image_filename="test_image.jpg",
                title=asset_title,
                caption=asset_caption)
            self.add_file_to_cleanup(asset.image.file.path)
        put_data = [
            {
                'asset_id': asset.asset_id
            },
        ]
        self.assertEqual(self.story.featured_assets.all().count(), 0)
        uri = '/api/0.1/assets/stories/%s/featured/' % (self.story.story_id)
        self.api_client.client.login(username=self.username, password=self.password)
        resp = self.api_client.put(uri, format='json', data=put_data)
        self.assertHttpAccepted(resp)
        # Refresh the story
        self.story = Story.objects.get(story_id=self.story.story_id)
        self.assertEqual(self.story.featured_assets.all().count(), 1)
        self.assertEqual(self.story.featured_assets.select_subclasses()[0],
                         asset)

    def test_put_list_unauthenticated(self):
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
                image_filename="test_image.jpg",
                title=asset_title,
                caption=asset_caption)
            self.add_file_to_cleanup(asset.image.file.path)
        put_data = [
            {
                'asset_id': asset.asset_id
            },
        ]
        self.assertEqual(self.story.featured_assets.all().count(), 0)
        uri = '/api/0.1/assets/stories/%s/featured/' % (self.story.story_id)
        resp = self.api_client.put(uri, format='json', data=put_data)
        self.assertHttpUnauthorized(resp)
        # Refresh the story
        self.story = Story.objects.get(story_id=self.story.story_id)
        self.assertEqual(self.story.featured_assets.all().count(), 0)

    def test_put_list_unauthorized(self):
        story = create_story(title="Test Story", summary="Test Summary",
            byline="Test Byline", status="published", language="en", 
            author=self.user2)
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
                image_filename="test_image.jpg",
                title=asset_title,
                caption=asset_caption)
            self.add_file_to_cleanup(asset.image.file.path)
        put_data = [
            {
                'asset_id': asset.asset_id
            },
        ]
        self.assertEqual(story.featured_assets.all().count(), 0)
        uri = '/api/0.1/assets/stories/%s/featured/' % (story.story_id)
        self.api_client.client.login(username=self.username, password=self.password)
        resp = self.api_client.put(uri, format='json', data=put_data)
        self.assertHttpUnauthorized(resp)
        # Refresh the story
        story = Story.objects.get(story_id=story.story_id)
        self.assertEqual(story.featured_assets.all().count(), 0)


class UtilsTest(TestCase):
    def test_image_type_supported_jpg(self):
        image_filename = "test_image.jpg"
        app_dir = os.path.dirname(os.path.abspath(__file__))
        img_path = os.path.join(app_dir, "test_files", image_filename)
        self.assertTrue(image_type_supported(img_path))
        
    def test_image_type_supported_pdf(self):
        image_filename = "test_image.pdf"
        app_dir = os.path.dirname(os.path.abspath(__file__))
        img_path = os.path.join(app_dir, "test_files", image_filename)
        self.assertFalse(image_type_supported(img_path))
