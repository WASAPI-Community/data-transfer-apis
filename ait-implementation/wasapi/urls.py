from rest_framework.routers import DefaultRouter
from archiveit.wasapi.views import WebdataQueryViewSet, JobsViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'webdata', WebdataQueryViewSet)
router.register(r'jobs', JobsViewSet)
urlpatterns = router.urls
