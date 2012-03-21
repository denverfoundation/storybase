from django.test import TestCase
from models import get_asset, Asset, HtmlAsset, HtmlAssetTranslation

class AssetModelTest(TestCase):
    def test_subclass(self):
        """ Test that Asset.subclass() returns the subclass of an Asset instance """
        asset = HtmlAsset()
        asset.save()
        translation = HtmlAssetTranslation(title="Test", asset=asset)
        translation.save()
        retrieved_asset = Asset.objects.get(pk=asset.pk)
        self.assertEqual(retrieved_asset.subclass(), asset)
        self.assertEqual(retrieved_asset.subclass().__class__.__name__, 'HtmlAsset')

    def test_license_name(self):
        asset = HtmlAsset(license='CC BY')
        asset.save()
        translation = HtmlAssetTranslation(title="Test", asset=asset)
        translation.save()
        self.assertEqual(asset.license_name(), 'Attribution Creative Commons')

class AssetApiTest(TestCase):
    def test_get_asset_return_subclass(self):
        """ Test that get_asset() returns the subclass of an Asset instance """
        asset = HtmlAsset()
        asset.save()
        translation = HtmlAssetTranslation(title="Test", asset=asset)
        translation.save()
        retrieved_asset = get_asset(asset_id=asset.asset_id)
        self.assertEqual(retrieved_asset, asset)
        self.assertEqual(retrieved_asset.__class__.__name__, 'HtmlAsset')
