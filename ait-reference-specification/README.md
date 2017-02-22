# **WASAPI Data Transfer API Archive-It Specification v1.0**


## Introduction

This document serves to specify Archive-It's implementation of v1.0 of the
Web Archive Data Export API.  It also proposes and assumes changes to the
minimum specification.


## Proposed changes to the published minimum

After more experience, we suggest that the minimum specification should be
adjusted.

### Pagination

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
SHA1.  To allow evolution, the specification should use an array instead of a
single checksum.  To ensure interoperability, all checksums should be
represented as hexadecimal strings.

### Change label describing format of archive file

Using the label `content-type` to describe the format of the archive files can
be confused with the "content-type" or "MIME-type" of the resources within the
archive.  The label `content-type` should be reserved as a potentially valuable
parameter to select such resources, and the current use should be replaced with
`filetype`.  Another label to consider is "archive-format" which explicitly
references its subject.


## Extensions beyond the published minimum

Archive-It extends the minimum with our own special parameters.

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



## Paths & Examples

### `/webdata`

   *(example: `https://partner.archive-it.org/export/v1/webdata`)*

The most basic query using the `/webdata` path returns a list of all web data
files on the server which are available to the client, basic metadata about
those files, and their download information. Parameters to modify `/webdata`
will be determined by institutions building their own implementations.
Potential parameters can be as simple as `/webdata?directoryName=[name]` or can
support an extensive list of parameters to modify a request. Examples of
possible parameters could include those defining identifiers for things like
collection, seed, crawl job, harvest event, session, date range,
archival identifier, administrative unit, repository, bucket, and more. All
institution-specific query filters and modifiers should be parameters to the
`/webdata` path.

   * **Example queries and results**

`https://partner.archive-it.org/export/v1/webdata?filename=2016-08-30-blah.warc.gz`

The above query would return a list of a single WARC file (though it may be
available from multiple mirrors).

```
{
    "includes-extra": false,
    "count": 1,
    "previous": null,
    "next": null,
    "files": [
        {
            "filename": "2016-08-30-blah.warc.gz",
            "filetype": "warc",
            "checksum": [
                "sha1:6b4f32a3408b1cd7db9372a63a2053c3ef25c731",
                "md5:766ba6fd3a257edf35d9f42a8dd42a79"
            ],
            "size": 8642688,
            "locations": [
                "http://archive-it.org/.../2016-08-30-blah.warc.gz"
            ]
        }
    ]
}
```

`https://partner.archive-it.org/export/v1/webdata?collection=456&crawl-start-after=2014-01-01&crawl-start-before=2016-01-01`

The above query would return a list of all the WARCs (with metadata and
download links) from between January 1, 2014 and December 31, 2015 for Collection 456.

```
{
    "includes-extra": false,
    "count": 1,
    "previous": null,
    "next": null,
    "files": [
        {
            "filename": "2016-08-30-blah.warc.gz",
            "filetype": "warc",
            "checksum": [
                "sha1:6b4f32a3408b1cd7db9372a63a2053c3ef25c731",
                "md5:766ba6fd3a257edf35d9f42a8dd42a79"
            ],
            "size": 8642688,
            "locations": [
                "http://archive-it.org/.../2014-01-01-blah.warc.gz",
                "/ipfs/QmaCpDMGvV3BGHeYERUEnRQAwe3N8SzbUtfsmvsqQLuvuJ"
            ]
        },
        {
            "filename": "2014-01-02-blah.warc.gz",
            "filetype": "warc",
            "checksum": [
                "sha1:8e4e78a274ffa59a972951b6a460791f92183ec8",
                "md5:5360dbc1187c433b948413bb9f0bd114"
            ],
            "size": 8519232,
            "locations": [
                "http://archive-it.org/.../2014-01-02-blah.warc.gz",
                "/ipfs/QmSoLju6m7xTh4DuokvT3886QRYqxAzb1kShaanJgW36yx"
            ]
        }
    ]
}
```

### `/jobs`

   *(example: `https://partner.archive-it.org/export/v1/jobs`)*

The `/jobs` path shows the jobs on this server accessible to the client. This
enables the request and deliver of WARC derivative webdata files. The `/jobs`
path supports GET and POST methods. Implementations that do not include the
ability to submit a job should still support his path and simply return that no
jobs are possible for the client on this server.

   * **Example queries and results**

`GET https://partner.archive-it.org/export/v1/jobs`

Results here depend on whether jobs have been submitted. If no jobs have been
submitted, you get an empty list. If you have submitted jobs, you get something
similar to the below.

```
{
    "count": 1,
    "previous": null,
    "next": null,
    "jobs": [
        {
            "jobtoken": "1440",
            "function": "build-wat",
            "query": "collection=456&crawl-start-after=2014-01-01&crawl-start-before=2016-01-01",
            "submit-time": "2016-12-08T16:05:44-0800",
            "termination-time": "2016-12-08T16:14:25-0800",
            "state": "complete"
        }
    ]
}


```

`POST https://partner.archive-it.org/export/v1/jobs`

The POST method includes a string matching a `/webdata` query string plus an
implementation-specific function available to the client. In this
specification, POST requests remain a bit of an abstraction, as they are
dependent upon the implementation-specific parameters supported under
`/webdata`.

Using the previous `/webdata` example, the below POST request would return a
job token for creating WATs for WARC files matching that `/webdata` query:

 `https://partner.archive-it.org/export/v1/jobs?collection=456&crawl-start-after=2014-01-01&crawl-start-before=2015-01-01&function=build-wat`

```
{
    "jobtoken": "1440",
    "function": "build-wat",
    "query": "collection=456&crawl-start-after=2014-01-01&crawl-start-before=2015-01-01",
    "submit-time": "2016-08-30Z15:52:53",
    "state": "queued"
}
```

### `/jobs/{jobToken}`

   *(example: `https://partner.archive-it.org/export/v1/jobs/123456`)*

The `/jobs/{jobToken}` path returns the status of a submitted job.

   * **Example queries and results**

`GET https://partner.archive-it.org/export/v1/jobs/123456`

Retrieve status for a submitted job, some metadata, including the original
query, time it was requested, whether it has completed ie current state, etc.

```
{
    "jobtoken": "1440",
    "function": "build-wat",
    "query": "collection=456&crawl-start-after=2014-01-01&crawl-start-before=2015-01-01",
    "submit-time": "2016-08-30Z15:52:53",
    "termination-time": "2016-08-30Z15:59:13",
    "state": "complete"
}
```


### `/jobs/{jobToken}/result`

   *(example: `https://partner.archive-it.org/export/v1/jobs/123456/result`)*

The `/jobs/{jobToken}` path returns the result of a complete job.

   * **Example queries and results**

`GET https://partner.archive-it.org/export/v1/jobs/123456/result`

Retrieve the result of a complete job. Results are not necessarily available
indefinitely. May return "410 Gone" if derivatives generated by this job have
been replaced (e.g. by the results of a newer job), or if job has been expired
by some other policy. An implementation may (but is not required to) make
results later available under /webdata queries.

```
{
    "includes-extra": false,
    "count": 2,
    "previous": null,
    "next": null,
    "files": [
        {
            "filename": "123456.0.wat",
            "filetype": "wat",
            "checksum": [
                "sha1:6b4f32a3408b1cd7db9372a63a2053c3ef25c731",
                "md5:766ba6fd3a257edf35d9f42a8dd42a79"
            ],
            "size": 42688,
            "locations": [
                "http://archive-it.org/.../123456.0.wat"
            ]
        },
        {
            "filename": "123456.1.wat",
            "filetype": "wat",
            "checksum": [
                "sha1:63439cd573560012dac9f78d5ddc29e66c5a3538",
                "md5:5360dbc1187c433b948413bb9f0bd114"
            ],
            "size": 26452,
            "locations": [
                "http://archive-it.org/.../123456.1.wat"
            ]
        }
    ]
}
```


## Contacts

*Internet Archive (Archive-It)*
* Jefferson Bailey, Director, Web Archiving, jefferson@archive.org
* Mark Sullivan, Web Archiving Software Engineer, msullivan@archive.org
