from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'(?P<filename>.*)', views.index, name='index'),
]
