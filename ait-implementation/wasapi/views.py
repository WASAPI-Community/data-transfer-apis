from rest_framework import viewsets
from rest_framework.response import Response
from archiveit.wasapi.serializers import WebdataFileSerializer, JobSerializer
from archiveit.wasapi.filters import WasapiAuthFilterBackend, FieldFilterBackend, WebdataMappedFieldFilterBackend
from archiveit.archiveit.models import WarcFile
from archiveit.wasapi.models import WasapiJob


class WebdataQueryViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows webdata files to be queried for and listed.
    """
    # TODO:  decide how to order results
    queryset = WarcFile.objects.all().order_by('-id')
    serializer_class = WebdataFileSerializer
    filter_backends = [
      WasapiAuthFilterBackend,
      FieldFilterBackend,
      WebdataMappedFieldFilterBackend]
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
        # The current implemenation doesn't support any query that could
        # include extra data, so we can hard-code False.  We must revisit
        # this as we add other queries.
        serializer.fields['includes-extra'] = WedgeValueIntoObjectField(
          value=False, label='includes-extra')
        return Response(serializer.data)


class JobsViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows WASAPI jobs to be created and monitored.
    """
    queryset = WasapiJob.objects.all().order_by('-id')
    serializer_class = JobSerializer
    filter_backends = [WasapiAuthFilterBackend]
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
