"""Views"""

from storybase.views.generic import ModelIdDetailView
from storybase_asset.models import Asset, DataSet

class AssetDetailView(ModelIdDetailView):
    context_object_name = "asset"
    queryset = Asset.objects.select_subclasses()
    template_name = 'storybase_asset/asset_detail.html'

class DataSetDetailView(ModelIdDetailView):
    context_object_name = "dataset"
    queryset = DataSet.objects.select_subclasses()
    template_name = 'storybase_asset/datasset_detail.html'
