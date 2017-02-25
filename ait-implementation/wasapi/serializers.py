from rest_framework import serializers
from archiveit.settings import WEBDATA_LOCATION_TEMPLATE
from archiveit.archiveit.models import WarcFile

class WebdataFileSerializer(serializers.HyperlinkedModelSerializer):
    filetype = serializers.CharField()
    checksum = serializers.CharField()
    account = serializers.SerializerMethodField('account_method')
    collection = serializers.PrimaryKeyRelatedField()
    crawl = serializers.IntegerField()
    crawl_start = serializers.SerializerMethodField('crawl_start_method')
    locations = serializers.SerializerMethodField('locations_method')
    def account_method(self, obj):
        return obj.account_id
    def crawl_start_method(self, obj):
        return obj.crawl_job.original_start_date
    def locations_method(self, obj):
        return [WEBDATA_LOCATION_TEMPLATE % obj.__dict__]
    class Meta:
        model = WarcFile
        fields = (
          'filename',
          'filetype',
          'checksum',
          'account',
          'size',
          'collection',
          'crawl',
          'crawl_start',
          'locations')
