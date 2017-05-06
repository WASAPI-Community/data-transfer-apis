from django.conf import settings
from django.core.exceptions import PermissionDenied
from rest_framework import serializers
from archiveit.archiveit.models import WarcFile
from archiveit.wasapi.models import WasapiJob

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
        crawl_job = obj.crawl_job
        return crawl_job and crawl_job.original_start_date
    def locations_method(self, obj):
        return [settings.WEBDATA_LOCATION_TEMPLATE % obj.__dict__]
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

class JobSerializer(serializers.HyperlinkedModelSerializer):

    state = serializers.CharField(read_only=True)
    account = serializers.PrimaryKeyRelatedField(read_only=True)
    jobtoken = serializers.SerializerMethodField('jobtoken_method')
    def jobtoken_method(self, obj):
        return str(obj.id)

    class Meta:
        model = WasapiJob
        fields = (
          'jobtoken',
          'function',
          'query',
          'submit_time',
          'termination_time',
          'state',
          'account')

    def validate(self, value):
        # I'd prefer to use a dedicated method rather than hooking into
        # validation routines, but my "to_internal_value" and "create" methods
        # don't get called.
        # It would be nice if we let each field set its value, but I don't see
        # an easy way to do that.
        value = self.set_state(value)
        value = self.set_account(value)
        return value

    def set_state(self, value):
        value['state'] = WasapiJob.QUEUED
        return value

    def set_account(self, value):
        account = self.context['request'].user.account
        if not account:  # eg "system" user
            raise PermissionDenied
        value['account'] = account
        return value
