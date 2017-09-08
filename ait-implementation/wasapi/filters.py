from rest_framework.filters import BaseFilterBackend
from archiveit.wasapi.selectors import select_webdata_query, select_auth

# A few words about selectors and "guts":  We want to share functionality
# between the "webdata" query and selecting the source files for a job, but
# those two clients have different information in different structures.
# Therefore, we extract (most of) the guts from the filter_queryset methods
# into functions in selectors.py, giving them a different interface (narrower
# than Django's, ie a querydict and kwargs that may or may not include an
# account that may or may not get used) which WasapiJob.set_ideal_result can
# use.

class WasapiWebdataQueryFilterBackend(BaseFilterBackend):
    """Filtering on composition necessary for the webdata query"""

    def filter_queryset(self, request, queryset, view):
        return select_webdata_query(request.GET, queryset,
          account=request.user.account, user=request.user)


class WasapiAuthFilterBackend(BaseFilterBackend):
    """Filtering on authorization"""
    def filter_queryset(self, request, queryset, view):
        return select_auth(request.GET, queryset,
          account=request.user.account, user=request.user)


class WasapiAuthJobBackend(BaseFilterBackend):
    """Filtering on authorization to see the specific job"""
    def filter_queryset(self, request, queryset, view):
        # TODO:   raise http error rather than empty result
        queryset = queryset.filter(job_id=view.kwargs['jobid'])
        if request.user.is_superuser:
            return queryset  # no restriction
        elif request.user.is_anonymous():
            return queryset.none()  # ie hide it all
        else:
            return queryset.filter(job__account=request.user.account)
