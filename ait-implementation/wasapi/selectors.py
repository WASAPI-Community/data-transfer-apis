# Functions that selectively filter a queryset, ie the "guts" of filters.

# Filtering functions, both abstract (could be in the DRF library) and specific
# to WASAPI, and composite


# for WasapiWebdataQueryFilterBackend and executing query of new WasapiJob
def select_webdata_query(querydict, queryset, **kwargs):
    sub_filters = [
      select_auth,
      select_wasapi_direct_fields,
      select_wasapi_mapped_fields,
    ]
    for filter in sub_filters:
        queryset = filter(querydict, queryset, **kwargs)
    return queryset


# for WasapiAuthFilterBackend
def select_auth(querydict, queryset, **kwargs):
    if kwargs['user'].is_superuser:
        return queryset  # no restriction
    if kwargs['user'].is_anonymous():
        return queryset.none()  # ie hide it all
    return queryset.filter(account_id=kwargs['account'].id)


def generate_select_direct_fields(*args):
    """Simple filtering on equality and inclusion of fields

    Any given field that is included in the class's multi_field_names is tested
    against any of potentially multiple arguments given in the request.  Any
    other (existing) field is tested for equality with the given value."""
    multi_field_names = set(args)
    def select_direct_fields(querydict, queryset, **kwargs):
        field_names = set( field.name for field in queryset.model._meta.get_fields() )
        for key, value in querydict.items():
            if key in multi_field_names:
                filter_value = { key+'__in': querydict.getlist(key) }
                queryset = queryset.filter(**filter_value)
            elif key in field_names:
                queryset = queryset.filter(**{ key:value })
        return queryset
    return select_direct_fields

# for WebdataDirectFieldFilterBackend
select_wasapi_direct_fields = generate_select_direct_fields('collection')


def generate_select_mapped_fields(filter_for_parameter):
    """Map parameters to ORM filters

    Based on `filter_for_parameter` dictionary mapping HTTP parameter name to
    ORM query filter"""

    def select_mapped_fields(querydict, queryset, **kwargs):
        for parameter_name, filter_name in filter_for_parameter.items():
            value = querydict.get(parameter_name)
            if value:
                queryset = queryset.filter(**{filter_name:value})
        return queryset
    return select_mapped_fields

# for WebdataMappedFieldFilterBackend
select_wasapi_mapped_fields = generate_select_mapped_fields({
  'crawl': 'crawl_job_id',
  'crawl-time-after': 'crawl_time__gte',
  'crawl-time-before': 'crawl_time__lt',
  'crawl-start-after': 'crawl_job__original_start_date__gte',
  'crawl-start-before': 'crawl_job__original_start_date__lt',
})
