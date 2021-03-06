from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.response import Response
from archiveit.wasapi.serializers import WebdataFileSerializer, PaginationSerializerOfFiles, JobSerializer, PaginationSerializerOfJobs
from archiveit.wasapi.filters import WasapiWebdataQueryFilterBackend, WasapiAuthFilterBackend, WasapiAuthJobBackend
from archiveit.archiveit.models import WarcFile
from archiveit.wasapi.models import WasapiJob, WasapiJobResultFile


class WebdataQueryViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows webdata files to be queried for and listed.
    """
    # TODO:  decide how to order results
    queryset = WarcFile.objects.all().order_by('-id')
    serializer_class = WebdataFileSerializer
    # selector shared with WasapiJob.query_just_like_webdataqueryviewset
    filter_backends = [WasapiWebdataQueryFilterBackend]
    pagination_serializer_class = PaginationSerializerOfFiles
    paginate_by_param = 'page_size'
    paginate_by = 100
    max_paginate_by = 2000

    def list(self, request, *args, **kwargs):
        """Cloned (but trimmed) from ModelViewSet.list"""
        self.object_list = self.filter_queryset(self.get_queryset())
        # always paginate our responses because that's how we implement the spec
        page = self.paginate_queryset(self.object_list)
        serializer = self.get_pagination_serializer(page)
        # The change to add other fields:
        # The current implementation doesn't support any query that could
        # include extra data, so we can hard-code False.  We must revisit
        # this as we add other queries.
        serializer.fields['includes-extra'] = WedgeValueIntoObjectField(
          value=False, label='includes-extra')
        serializer.fields['request-url'] = WedgeValueIntoObjectField(
          value=request._request.build_absolute_uri(), label='request-url')
        return Response(serializer.data)


class JobsViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows WASAPI jobs to be created and monitored.
    """
    queryset = WasapiJob.objects.all().order_by('-id')
    serializer_class = JobSerializer
    filter_backends = [WasapiAuthFilterBackend]
    pagination_serializer_class = PaginationSerializerOfJobs
    paginate_by_param = 'page_size'
    paginate_by = 100
    max_paginate_by = 2000


def update_result_file_state(request, filename):
    result_files = WasapiJobResultFile.objects.filter(filename=filename)
    if not result_files:
        return HttpResponse("", status=404)
    WasapiJobResultFile.update_states(result_files)
    return HttpResponse("")


class JobResultViewSet(viewsets.ModelViewSet):
    """
    API endpoint that gives the result of a WASAPI job.
    """
    queryset = WasapiJobResultFile.objects.all().order_by('-id')
    serializer_class = WebdataFileSerializer
    filter_backends = [
      WasapiAuthJobBackend
      # don't need WasapiAuthFilterBackend since we already filtered on the job
    ]
    pagination_serializer_class = PaginationSerializerOfFiles
    paginate_by_param = 'page_size'
    paginate_by = 100
    max_paginate_by = 2000


class WedgeValueIntoObjectField(object):
    read_only = False
    def __init__(self, value, label):
        self.value = value
        self.label = label
    def initialize(self, parent, field_name):
        pass
    def field_to_native(self, obj, field_name):
        return self.value
