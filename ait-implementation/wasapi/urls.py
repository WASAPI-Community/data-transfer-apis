from rest_framework.routers import DefaultRouter
from archiveit.wasapi.views import WebdataQueryViewSet

router = DefaultRouter()
router.register(r'webdata', WebdataQueryViewSet)
urlpatterns = router.urls
