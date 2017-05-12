from django.conf import settings
from django.core.exceptions import PermissionDenied
from rest_framework import serializers
from rest_framework.pagination import PaginationSerializer
from archiveit.archiveit.models import WarcFile
from archiveit.wasapi.models import WasapiJob

class WebdataFileSerializer(serializers.HyperlinkedModelSerializer):
    # explicitly adding to locals() lets us include '-' in name of fields
    locals().update({
      'filetype': serializers.SerializerMethodField('filetype_method'),
      'checksums': serializers.SerializerMethodField('checksums_method'),
      'account': serializers.SerializerMethodField('account_method'),
      'collection': serializers.PrimaryKeyRelatedField(),
      'crawl': serializers.IntegerField(),
      'crawl-start': serializers.SerializerMethodField('crawl_start_method'),
      'locations': serializers.SerializerMethodField('locations_method')})
    def filetype_method(self, obj):
        return "warc"
    def checksums_method(self, obj):
        return {
          'sha1': obj.sha1,
          'md5': obj.md5 }
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
          'checksums',
          'account',
          'size',
          'collection',
          'crawl',
          'crawl-start',
          'locations')

class PaginationSerializerOfFiles(PaginationSerializer):
    'Pagination serializer that labels the "results" as "files"'
    results_field = 'files'


class JobSerializer(serializers.HyperlinkedModelSerializer):

    # explicitly adding to locals() lets us include '-' in name of fields
    locals().update({
      'state': serializers.CharField(read_only=True),
      'account': serializers.PrimaryKeyRelatedField(read_only=True),
      'jobtoken': serializers.SerializerMethodField('jobtoken_method'),
      'submit-time': serializers.DateTimeField(source='submit_time'),
      'termination-time': serializers.DateTimeField(source='termination_time')})

    def jobtoken_method(self, obj):
        return str(obj.id)

    class Meta:
        model = WasapiJob
        fields = (
          'jobtoken',
          'function',
          'query',
          'submit-time',
          'termination-time',
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

class PaginationSerializerOfJobs(PaginationSerializer):
    'Pagination serializer that labels the "results" as "jobs"'
    results_field = 'jobs'
