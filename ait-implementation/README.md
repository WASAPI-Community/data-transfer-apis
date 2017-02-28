# Archive-It WASAPI implementation

The `archiveit/wasapi` application is the bulk of the code by which Archive-It implements the WASAPI specification.  It was written within and then extracted from the [Django](https://www.djangoproject.com/) project (version 1.8.5) that serves [Archive-It's partner site](https://partner.archive-it.org/), so --while it can not be run alone-- it can be fit easily into another Django project.


## Formal specifications

The [OpenAPI](https://www.openapis.org/) file `wasapi/swagger.yaml` describes Archive-It's ideal specification at the start of implementation (with few adjustments).  The file `wasapi/implemented-swagger.yaml` shows what has been implemented.  The difference between the two serves as a to-do list:  note particularly that jobs are not yet implemented.


## Re-integrating the code

To use the `wasapi` application within another Django project, you must resolve some references it has to the Archive-It project.

Archive-It's webdata files are modeled in `archiveit.archiveit.models.WarcFile`; replace that with your own.

The URL paths to the WASAPI endpoints (and also transport of webdata files) were established in `archiveit/urls.py`; add your own reference to your own routing file (as appropriate for the version of Django you are using):

    urlpatterns = (
      # [...]
      patterns('',
        # [...]
        url(r'^wasapi/v1/', include('archiveit.wasapi.urls')),
        url(r'^webdatafile/', include('archiveit.webdata.urls')),
      )
    )

The full URL to transport a webdata file was defined by WEBDATA_LOCATION_TEMPLATE in `archiveit.settings`.  It uses named parameters from the webdata file model, eg `filename`.  Make your own, eg:

    WEBDATA_LOCATION_TEMPLATE = BASEURL + '/webdatafile/%%(filename)s'


## The `webdata` application

The `archiveit/webdata` application implements transport of webdata files.  That is outside the scope of the WASAPI specification, but we include it here for completeness.  It transparently serves webdata files from Archive-It's Petabox and HDFS stores.
