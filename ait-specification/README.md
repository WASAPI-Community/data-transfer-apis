# **Archive-It WASAPI Data Transfer API v1.0**


## Introduction

This document serves to specify v1.0 of Archive-It's implementation of the WASAPI Data Transfer API.  It is intended to document how a client can use the API to find and select web archive files for transfer and to submit jobs for the creation and transfer of derivative web archive files. The API is designed according to the WASAPI data transfer [general specification](https://github.com/WASAPI-Community/data-transfer-apis/tree/master/general-specification). For context, as of June 2017 the Archive-It repository contains over 3,766,068 WARC files, all of which are accessible to the relevant, authenticated Archive-It partners via this API.

The interface provides two primary services:  querying existing files and managing jobs for creating derivative files. The WASAPI data transfer general specification does not mandate how to transfer the webdata files for export, but Archive-It's implementation provides straight-forward HTTPS links. We use the syntax `webdata` file to recognize that the API supports working with both web archive files (WARCs) as well as with derivative files created from WARCs (such as WATs or CDX).

## Authentication

Archive-It restricts access to those clients with an Archive-It account.  The WASAPI data transfer general specification allows publicly accessible resources, so Archive-It's implementation will show empty results until you authenticate.  You have two options for authentication:

### Authentication via browser cookies

To try some simple queries or manually download your data with a web browser, you can authenticate with cookies in your web browser.

Point your web browser to `https://partner.archive-it.org/login` and log in to your Archive-It account with your username and password.  This will set cookies in your browser for subsequent WASAPI requests and downloading files.

### Authentication via basic access authentication

For automated scripts, you should use http [basic access authentication](https://en.wikipedia.org/wiki/Basic_access_authentication).

For example, if your account has username `teddy` and password `schellenberg`, you could use this [cURL](https://curl.haxx.se/) invocation:

    curl --user 'teddy:schellenberg' https://partner.archive-it.org/wasapi/v1/webdata

## Querying

Archive-It's data transfer API implementation, Archive-It lets you identify the webdata files via a number of parameters. Start building the URL for your query with `https://partner.archive-it.org/wasapi/v1/webdata`, then append parameters to make your specific query.

To find all webdata files in your account:

    https://partner.archive-it.org/wasapi/v1/webdata

### Overview of Query Parameters

The basic parameters for querying for webdata files are:

- `filename`: the exact webdata filename
- `filetype`:  the exact webdata files of a specific type, eg `warc`, `wat`, `cdx`
- `collection`: Archive-It collection identifier
- `crawl`: Archive-It crawl job identifier
- `crawl-time-after` & `crawl-time-before`: date of webdata file creation during a crawl job
- `crawl-start-after` & `crawl-start-before`: date of crawl job start

### Query parameters

#### `filename` query parameter

The `filename` parameter restricts the query to include webdata files with the exact filename as the parameter's value.  That is, it must match the beginning and end of the filename; the full path of directories is ignored. API v1.0 matches exact filenames, but later version will recognize "globbing," i.e. matching with `*` and `?` patterns.

To find a specific file:

    https://partner.archive-it.org/wasapi/v1/webdata?filename=ARCHIVEIT-8232-WEEKLY-JOB300208-20170513202120098-00001.warc.gz

#### `filetype` query parameter

The `filetype` parameter restricts the query to those web archive files with the specified type, such as `warc`, `wat`, `cdx`.  API v1.0 supports query by `warc` and later version will support query by derivative formats.

#### `collection` query parameter

The `collection` parameter restricts the query to those web archive files within the specified collection. Archive-It users may want to reference the documentation on how to [find your collection's ID number](https://support.archive-it.org/hc/en-us/articles/208000916-Find-your-collection-s-ID-number).

To find the files from the "Occupy Movement 2011/2012" collection:

    https://partner.archive-it.org/wasapi/v1/webdata?collection=2950

The API supports multiple `collection` parameters in a query. To find the files from the "Occupy Movement 2011/2012" collection and the "#blacklivesmatter Web Archive" collection:

    https://partner.archive-it.org/wasapi/v1/webdata?collection=2950&collection=4783

#### `crawl` query parameter

The `crawl` parameter restricts the query to webdata files within a specified crawl, per the crawl job identifier. Archive-It users may want to reference the documentation on [how to find a crawl ID number](https://support.archive-it.org/hc/en-us/articles/115002803383-Finding-your-crawl-ID-number-). Some older Archive-It WARCs and webdata files lack an associated crawl job ID (and, thus, also an associated `crawl-start-time`). Efforts are underway to backfill this data, which should alleviate, if not eliminate, the null values for `crawl` for some historical WARCs. If users receive null results for a know `crawl` identifier, they should contact Archive-It support or use other parameters, which are known to be exhaustive historically.

To find the files from a specific crawl:

    https://partner.archive-it.org/wasapi/v1/webdata?crawl=300208

#### `crawl-time-after` and `crawl-time-before` query parameters

The `crawl-time-after` and `crawl-time-before` parameters restrict the query to those web archive files crawled within the given time range; see [time formats](#time-formats) for the syntax. Specify the lower bound (if any) with `crawl-time-after` and the upper bound (if any) `crawl-time-before`.  This field uses the time the WARC file was created, the same timestamp represented in the WARC filename.

To find the files crawled in the first quarter of 2016:

    https://partner.archive-it.org/wasapi/v1/webdata?crawl-time-after=2016-12-31&crawl-time-before=2016-04-01

To find all files crawled since 2016:

    https://partner.archive-it.org/wasapi/v1/webdata?crawl-time-after=2016-01-01

To find all files crawled prior to 2014:

    https://partner.archive-it.org/wasapi/v1/webdata?crawl-time-before=2014-01-01

#### `crawl-start-after` and `crawl-start-before` query parameters

The `crawl-start-after` and `crawl-start-before` parameters restrict the query to those web archive files gathered from crawl jobs that started within the given time range; see [time formats](#time-formats) for the syntax.  They reference the crawl job start date (in contrast to `crawl-time-after` and `-before` which relate to the individual WARC file creation date).  Specify the lower bound (if any) with `crawl-start-after` and the upper bound (if any) `crawl-start-before`. Since `crawl-start` is associated with the `crawl` parameter, the above caveats will apply in that some older Archive-It WARCs and web archive files will lack an associated `crawl-start`. Efforts are underway to backfill this data, otherwise contact Archive-It support or use other parameters, which are known to be exhaustive historically.

To find the files from a Q1 2016 crawl:

      https://partner.archive-it.org/wasapi/v1/webdata?crawl-start-after=2016-12-31&crawl-start-before=2016-04-01

To find all files from crawls started since 2016:

    https://partner.archive-it.org/wasapi/v1/webdata?crawl-start-after=2016-01-01

#### Pagination parameters

The [parameters for pagination](#parameters-for-pagination) apply to queries.

### Query results

The response to a query is a JSON object with [fields for pagination](#fields-for-pagination), an `includes-extra` field, a `request-url` field, and the result in the `files` field.

The `count` field represents the total number of web archive files corresponding to the query.

The `includes-extra` field is currently always false in the API v1.0, as all query parameters return exact matches and the data in the `files` contains nothing extraneous from what is necessary to satisfy the query or job. The `includes-extra` field is mandated by the general specification as some implementations may return results that include webdata files containing content beyond the specific query. For instance, were `url` a query parameter, a request by URL could return results that contain webdata files (i.e. WARCs) that contain data from that URL as well as data from other URLs, due to the way crawlers write WARC files. When Archive-It (or other implementations) supports these type queries, `includes-extra` could have a true value to indicate that the referenced `files` may contain data outside the specific query.

The `request-url` field represents the submitted query URL.

The `files` field is a list of a subset (check the [pagination fields](#fields-for-pagination)) of the results of the query, with each webdata file represented by a JSON object with the following keys:

- `account`:  the numeric Archive-It account identifier

- `checksums`:  an object with `md5` and `sha1` keys and hexadecimal values of
  the webdata file's checksums

- `collection`:  the numeric Archive-It identifier of the collection that includes the
  webdata file

- `crawl`:  the numeric Archive-It identifier of the crawl that created the webdata file

- `crawl-start`:  an optional RFC3339 date stamp of the time the crawl job started

- `crawl-time`:  an RFC3339 date stamp of the time the webdata file was
  [created](#crawl-time-after-and-crawl-time-before-query-parameters)

- `filename`:  the name of the webdata file (without any path of directories)

- `filetype`:  the format of the webdata file, eg `warc`, `wat`, `wane`, `cdx`

- `locations`:  a list of sources from which to retrieve the webdata file

- `size`:  the size in bytes of the webdata file

For example:

    {
      "count": 601,
      "includes-extra": false,
      "next": "https://partner.archive-it.org/wasapi/v1/webdata?collection=8232&page=2",
      "previous": null,
      "files": [
        {
          "account": 89,
          "checksums": {
            "md5": "073f2a905ce23462204606329ca545c3",
            "sha1": "1b796f61dc22f2ca246fa7055e97cd25341bfe98"
          },
          "collection": 8232,
          "crawl": 304244,
          "crawl-start": "2017-05-31T22:15:34Z",
          "crawl-time": "2017-05-31T22:15:40Z",
          "filename": "ARCHIVEIT-8232-WEEKLY-JOB304244-20170531221540622-00000.warc.gz",
          "filetype": "warc",
          "locations": [
            "https://warcs.archive-it.org/webdatafile/ARCHIVEIT-8232-WEEKLY-JOB304244-20170531221540622-00000.warc.gz"
          ],
          "size": 1000000858
        },
        {
          "account": 89,
          "checksums": {
            "md5": "610e1849cfc2ad692773348dd34697b4",
            "sha1": "9048d063a9adaf606e1ec2321cde3a29a1ee6490"
          },
          "collection": 8232,
          "crawl": 303042,
          "crawl-start": "2017-05-24T22:15:36Z",
          "crawl-time": "2017-05-26T17:51:37Z",
          "filename": "ARCHIVEIT-8232-WEEKLY-JOB303042-20170526175137981-00002.warc.gz",
          "filetype": "warc",
          "locations": [
            "https://warcs.archive-it.org/webdatafile/ARCHIVEIT-8232-WEEKLY-JOB303042-20170526175137981-00002.warc.gz"
          ],
          "size": 40723812
        },
        [ ... ]
      ]
    }


## Jobs

The Archive-It data transfer API allows users to submit "jobs" for the creation of derivative files from existing resources. This serves the broader goal of WASAPI data transfer APIs to facilitate use of web archives in data-driven scholarship, research and computational analysis, and to support use, and transport, of files derived from WARCs and original archival web data. The Archive-It WASAPI data transfer API v1.0 allows an Archive-It user or approved researcher to:

- Submit a query and be returned a results list of webdata files
- Submit a job to derive different types of datasets from that results list
- Receive a job submission token and job submission status
- Poll the API for current job status
- Upon job completion, get a results list of the generated derived webdata files

### Submitting a new job

Submit a new job with an HTTP POST to `https://partner.archive-it.org/wasapi/v1/jobs`.

Select a `function` from those supported. The Archive-It API v1.0 currently supports creation of three types of derivative datasets, all of which have a one-to-one correlation to WARC files. Future development will allow for job submission for original datasets. The current job `function` list:

- `build-wat`: build a WAT (Web Archive Transformation) file from the matched web archive files

- `build-wane`: build a WANE (Web Archive Name Entities) file from the matched  web archive files 

- `build-cdx`: Build a CDX (Capture Index) file from the matched  web archive files

For more on WATs and WANEs, see their description at [Archive-It Research Services](https://webarchive.jira.com/wiki/display/ARS/Archive-It+Research+Services). For more on CDX, see the documentation for the [CDX Server API](https://github.com/internetarchive/wayback/blob/master/wayback-cdx-server/README.md).

Build an appropriate `query` in the same manner as for the [`/webdata` endpoint](#query-parameters).

For example, to build WAT files from the WARCs in Collection 4783 and crawled in 2016: 

    curl --user 'teddy:schellenberg' -H 'Content-Type: application/json' -d '{"function": "build-wat","query": "collection=4783&crawl-time-after=2016-01-01&crawl-time-before=2017-01-01"}' https://partner.archive-it.org/wasapi/v1/jobs

If all goes well, the server will record the job, set its `submit-time` to the current time and its `state` to `queued`, and return a `201 Created` response, including a `jobtoken` which can be used to [check its
status](#checking-the-status-of-a-job) later:

    {
      "account": 89,
      "function": "build-wat",
      "jobtoken": "136",
      "query": "collection=4783&crawl-time-after=2016-01-01&crawl-time-before=2017-01-01",
      "state": "queued",
      "submit-time": "2017-06-03T22:49:13.869698Z",
      "termination-time": null
    }

If you want to match everything, you must still provide an explicit empty string for the query parameter.  For example, to build a CDX index of all your resources:

    curl --user 'teddy:schellenberg' -H 'Content-Type: application/json' -d '{"function":"build-cdx","query":""}' https://partner.archive-it.org/wasapi/v1/jobs

### Checking the status of a job

To check the [state](#states-of-a-job) of your job, build a URL by appending its job token to `https://partner.archive-it.org/wasapi/v1/jobs/`.  For example:

    curl --user 'teddy:schellenberg' https://partner.archive-it.org/wasapi/v1/jobs/136

Immediately after submitting it, the job will be in the `queued` `state`, and the response will be the same as the response to the submission.  Once Archive-It starts running the job, its `state` will change, for example:

    {
      "account": 89,
      "function": "build-wat",
      "jobtoken": "136",
      "query": "collection=4783&crawl-time-after=2016-01-01&crawl-time-before=2017-01-01",
      "state": "running",
      "submit-time": "2017-06-03T22:49:13Z",
      "termination-time": null
    }

And when it is `complete`, the `termination-time` will be set with the time:

    {
      "account": 89,
      "function": "build-wat",
      "jobtoken": "136",
      "query": "collection=4783&crawl-time-after=2016-01-01&crawl-time-before=2017-01-01",
      "state": "complete",
      "submit-time": "2017-06-03T22:49:13Z",
      "termination-time": "2017-06-06T01:37:54Z"
    }

You can also check the [states](#states-of-a-job) of all your jobs at `https://partner.archive-it.org/wasapi/v1/jobs`, which is [paginated](Pagination).  For example:

    {
      "count": 16,
      "next": "http://partner.archive-it.org/wasapi/v1/jobs?page_size=10&page=2",
      "previous": null,
      "jobs": [
        {
          "account": 89,
          "function": "build-cdx",
          "jobtoken": "137",
          "query": "",
          "state": "running",
          "submit-time": "2017-06-03T23:55:51Z",
          "termination-time": null
        },
        {
          "account": 89,
          "function": "build-wat",
          "jobtoken": "136",
          "query": "collection=4783&crawl-time-after=2016-01-01&crawl-time-before=2017-01-01",
          "state": "completed",
          "submit-time": "2017-06-03T22:49:13Z",
          "termination-time": "2017-06-06T01:37:54Z"
        },
        [ ... ]
      ]
    }

### Checking the result of a failed job

If your job has a `failed` `state`, build a URL of the form `https://partner.archive-it.org/wasapi/v1/jobs/{jobtoken}/error`.  This is in development and not currently implemented.

### Checking the result of a complete job

To retrieve the result of your `complete` job, build a URL of the form
`https://partner.archive-it.org/wasapi/v1/jobs/{jobtoken}/result`.  This is in development and not yet implemented. Once implemented, the results of jobs will be able to be queried by filetype and by job result.

## Common WASAPI infrastructure

### Pagination

Results of queries and lists of jobs are paginated.  The full results may fit on one page (especially if you set `page_size=2000`), but the syntax is always present.  You needn't manipulate the `page` parameter directly:  after your first request with no `page` parameter, you should iteratively follow non-null `next` links to fetch the full results.

#### Fields for pagination

The top-level JSON object of the response includes pagination information with the following keys:

- `count`:  The number of items in the full result (files or jobs, across all
  pages)

- `previous`:  Link (if any) to the previous page of items; otherwise null

- `next`:  Link (if any) to the next page of items; otherwise null

#### Parameters for pagination

##### `page` query parameter

The `page` parameter requests a specific page of the full result.  It defaults to 1, giving the first page.

##### `page_size` query parameter

The `page_size` parameter sets the size of each page.  It defaults to 100 and has a maximum value of 2000.

### Time formats

Date and time parameters should satisfy RFC3339, eg `YYYY-MM-DD` or `YYYY-MM-DDTHH:MM:SS`, but Archive-It also recognizes abbreviations like `YYYY-MM` or `YYYY` which are interpreted as the first of the month or year.  We recommend using [UTC](https://en.wikipedia.org/wiki/Coordinated_Universal_Time), but the implementation does now recognize a trailing `Z` or timezone offset.

Formats that work:
- `2017-01-01`
- `2017-01-01T12:34:56`
- `2017-01-01 12:34:56`
- `2017-01-01T12:34:56Z`
- `2017-01-01 12:34:56-0700`
- `2017`
- `2017-01`

## Recipes and other resources

Archive-It is in the midst of creating a recipe book of sample API queries. Both Archive-It and WASAPI grant partners are also creating a number of local utilities for working with this API and implementing it in preservation and research workflows. These utilities will also be posted in this GitHub account for public reference. Stanford has created a number of demonstration videos outlining their tool development for working with this API for ingest of their Archive-It WARCs into their preservation repository. These can be seen in the [WASAPI collection](https://archive.org/details/wasapi) in the Internet Archive and Stanford Libraries' [YouTube channel](https://www.youtube.com/channel/UCc2CQuHkhKGZ-2ZLTZVGE2A).

For Archive-It's proposed changes to the WASAPI data transfer API general specification and other build details, visit the [Archive-It implementation repository](https://github.com/WASAPI-Community/data-transfer-apis/tree/master/ait-implementation).

## Contacts

*Archive-It (Internet Archive)*
* Jefferson Bailey, Director, Web Archiving, jefferson@archive.org
* Mark Sullivan, Web Archiving Software Engineer, msullivan@archive.org
