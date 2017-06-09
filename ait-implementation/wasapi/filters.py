from rest_framework.filters import BaseFilterBackend


class WasapiAuthFilterBackend(BaseFilterBackend):
    """Filtering on authorization"""

    def filter_queryset(self, request, queryset, view):
        if request.user.is_superuser:
            return queryset  # no restriction
        if request.user.is_anonymous():
            return queryset.none()  # ie hide it all
        return queryset.filter(account_id=request.user.account_id)


class FieldFilterBackend(BaseFilterBackend):
    """Simple filtering on equality and inclusion of fields

    Any given field that is included in the class's multi_field_names is tested
    against any of potentially multiple arguments given in the request.  Any
    other (existing) field is tested for equality with the given value."""

    multi_field_names = set()
    def filter_queryset(self, request, queryset, view):
        field_names = set( field.name for field in queryset.model._meta.get_fields() )
        for key, value in request.GET.items():
            if key in self.multi_field_names:
                filter_value = { key+'__in': request.QUERY_PARAMS.getlist(key) }
                queryset = queryset.filter(**filter_value)
            elif key in field_names:
                queryset = queryset.filter(**{ key:value })
        return queryset


class WebdataFieldFilterBackend(FieldFilterBackend):
    multi_field_names = {'collection'}


class MappedFieldFilterBackend(BaseFilterBackend):
    """Map parameters to ORM filters

    Based on `filter_for_parameter` dictionary mapping HTTP parameter name to
    ORM query filter"""

    def filter_queryset(self, request, queryset, view):
        for parameter_name, filter_name in self.filter_for_parameter.items():
            value = request.GET.get(parameter_name)
            if value:
                queryset = queryset.filter(**{filter_name:value})
        return queryset


class WebdataMappedFieldFilterBackend(MappedFieldFilterBackend):
    """Wasapi-specific queries beyond what DRF provides"""
    filter_for_parameter = {
      'crawl': 'crawl_job_id',
      'crawl-time-after': 'crawl_time__gte',
      'crawl-time-before': 'crawl_time__lt',
      'crawl-start-after': 'crawl_job__original_start_date__gte',
      'crawl-start-before': 'crawl_job__original_start_date__lt',
    }
