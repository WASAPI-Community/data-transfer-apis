from django.core.urlresolvers import RegexURLPattern
from rest_framework.routers import DefaultRouter
from archiveit.wasapi.views import WebdataQueryViewSet, JobsViewSet, update_result_file_state, JobResultViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'webdata', WebdataQueryViewSet)
router.register(r'jobs/(?P<jobid>\d+)/result', JobResultViewSet)
router.register(r'jobs', JobsViewSet)
router.urls.append(RegexURLPattern(r'^update_result_file_state/(?P<filename>.*)', update_result_file_state))
urlpatterns = router.urls
