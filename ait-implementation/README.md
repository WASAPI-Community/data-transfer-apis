# Archive-It WASAPI implementation

The `archiveit/wasapi` application is the bulk of the code by which Archive-It implements the WASAPI specification.  It was written within and then extracted from the [Django](https://www.djangoproject.com/) project (version 1.8.5) that serves [Archive-It's partner site](https://partner.archive-it.org/), so --while it can not be run alone-- it can be fit easily into another Django project. This document outlines implementation details, proposed changes to the WASAPI Data Transfer API general specificiation and the Archive-It additions beyond the minimum specifications.


## Formal specifications

The [OpenAPI](https://www.openapis.org/) file `wasapi/swagger.yaml` describes Archive-It's ideal specification at the start of implementation (with few adjustments).  The file `wasapi/implemented-swagger.yaml` shows what has been implemented.  The difference between the two serves as a to-do list:  note that you can submit new jobs and monitor their status but not yet retrieve their results.


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


## The notification mailer and admin interface

To fit with Archive-It's existing work flow, the implementation sends a notification email upon submission of a new job.  We also provide [Django admin site](https://docs.djangoproject.com/en/dev/ref/contrib/admin/) to change the state of jobs.  This is outside the scope of the WASAPI specification, but we include it here for completeness.

## The `webdata` application

The `archiveit/webdata` application implements transport of webdata files.  That is well outside the scope of the WASAPI specification, but we include it here also for completeness.  It transparently serves webdata files from Archive-It's Petabox and HDFS stores.


## Proposed changes to the published minimum

After more experience, we suggest that the minimum specification should be
adjusted.

### Mandatory pagination syntax

The specification should support pagination of large results.  Simple
implementations may give the full results in a single page, but adding the
syntax later would be difficult.

Unable to find consistent recommendations for pagination syntax, we adopt that
of the [Django Rest Framework](http://www.django-rest-framework.org/).  The
client must accept `count`, `previous`, and `next` parameters.  The
implementation must provide the number of files/jobs/etc in `count`.  The
`previous` and `next` values can be either URLs by which to fetch other pages
of results using a `page` parameter, be absent, or (as the Django Rest
Framework does) hold an explicit `null`.

### Matching filenames

Matching of filenames should consider only the basename and not any path of
directories.  The glob pattern should be matched against the complete basename
(ie must match the beginning and end of the filename).  An implementation that
wants to match pathnames including directories (and consider eg whether `**`
should match multiple directory separators eg `/`) may offer a different
parameter.

### Simpler webdata file bundles

We should drop `WebdataMenu` and `WebdataBundle`.  The multiple `locations` of
a `WebdataFile` provide most of their value.  Rather than giving the client
more information than would be used, an implementation can accept a request for
specific transports and formats.

### Separate endpoint for results of a job; reporting on a failed job

We replace `completion-time` with `termination-time` to ease polling for new
information about jobs.  Rather than a job that may include a successful result
but gives the same indistinguishable lack of result for both progress and
failure, we provide distinct endpoints:  `/jobs/{jobtoken}/result` for a
successful result and `/jobs/{jobtoken}/error` for reporting the error of a
failed job.  A client can easily poll `/jobs/{jobtoken}/result` and will be
redirected to `/jobs/{jobtoken}/error` in the case that the job fails.

### Checksums of a webdata file

Since it is useless to require the presence of checksums without mandating any
specific checksum, every implementation should provide at least one of MD5 or
SHA1.  To allow evolution, the specification should use a dictionary instead of
a single string.  To ensure interoperability, all checksums should be
represented as hexadecimal strings.

### Change label describing format of archive file

Using the label `content-type` to describe the format of the archive files can
be confused with the "content-type" or "MIME-type" of the resources within the
archive.  The label `content-type` should be reserved as a potentially valuable
parameter to select such resources, and the current use should be replaced with
`filetype`.  Another label to consider is "archive-format" which explicitly
references its subject.


## Extensions beyond the published minimum

Archive-It extends the minimum specification with our own special parameters for our v1.0 release.

### Time range parameters

We want to support date ranges, but we want to be careful about which time we
refer to:  the instant the crawl was requested, the instant a delayed crawl was
scheduled to start, the instant the crawl started, the instant the resource is
retrieved, the instant the archive file was written.  For ease of
implementation, we choose to operate on the time that the crawl started using
the `crawl-start-after` and `crawl-start-before` parameters.

### Collection parameter

The `collection` parameter accepts a numeric collection identifier as is used
in the Archive-It application.

### Crawl parameter

The `crawl` parameter accepts a numeric crawl identifier as is used in the
Archive-It application.

### Functions

Archive-It supports jobs of three functions:
- `build-wat`:  Build a WAT file with metadata from the matched archive files
- `build-wane`:  Build a WANE file with the named entities from the matched
  archive files
- `build-cdx`:  Build a CDX file indexing the matched archive files

Archive-It functions do not yet accept any parameters.

### States of a job

An Archive-It job can be described as being in one of five distinct states:
- `queued`:  Job has been submitted and is waiting to run.
- `running`:  Job is currently running.
- `failed`:  Job ran but failed.
- `complete`:  Job ran and successfully completed; result is available.
- `gone`:  Job ran, but the result is no longer available (eg deleted to save
  storage).

## Contacts

*Archive-It (Internet Archive)*
* Jefferson Bailey, Director, Web Archiving, jefferson@archive.org
* Mark Sullivan, Web Archiving Software Engineer, msullivan@archive.org
