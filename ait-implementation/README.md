# Archive-It WASAPI implementation

The `archiveit/wasapi` app is the bulk of the code by which Archive-It implements the WASAPI specification.  It was written within and then extracted from the [Django project  
] that serves [ 
Archive-It's partner site], so --while it can not be run alone-- it can be fit easily into another Django project.


## The `wasapi` app



contains the implementation of the WASAPI. 

## Formal specifications

The [OpenAPI ] 
file `wasapi/swagger.yaml` describes Archive-It's ideal specification at the start of implementation (with few adjustments).  The file `wasapi/implemented-swagger.yaml` shows what has been implemented.  The difference between the two serves as a to-do list:  note particularly that jobs are not implemented.

### Re-integrating the code

To use the `wasapi` app within another Django application.
  Note that this was written using Django version 1.8.5.


+WEBDATA_LOCATION_TEMPLATE = '%s/webdatafile/%%(filename)s' % BASE50URL

+    url(r'^wasapi/v1/', include('archiveit.wasapi.urls')),
+    url(r'^webdatafile/', include('archiveit.webdata.urls')),


## The `webdata` app

The `archiveit/webdata` app implements transport of webdata files.  That is outside the scope of the WASAPI specification, but we include it here for completeness.  It serves webdata files from Archive-It's Petabox and HDFS stores.
