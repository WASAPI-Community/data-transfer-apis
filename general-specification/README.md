## **WASAPI Data Transfer API General Specification v0.1**

**Introduction**

   This document serves to outline v0.1 of the Web Archive Data Export API developed as part of the Web Archiving Systems API (WASAPI) project of the [Institute of Museum and Library Services](https://www.imls.gov/)-funded [National Leadership Grant, LG-71-15-0174](https://www.imls.gov/grants/available/national-leadership-grants-libraries), "[Systems Interoperability and Collaborative Development for Web Archiving](https://www.imls.gov/sites/default/files/proposal_narritive_lg-71-15-0174_internet_archive.pdf)" (PDF). Primary development of this API specification as well as the creation of multiple reference implementations is being led by Internet Archive (Archive-It) and Stanford University Libraries (DLSS and LOCKSS). Other project partners are University of North Texas, Rutgers University, a Technical Working Group, and an Advisory Board. More information on the WASAPI project can be found at the [WASAPI-Community Github workspace](https://github.com/WASAPI-Community) the [WASAPI-community Google Group](https://groups.google.com/forum/#!forum/wasapi-community), and on the [WASAPI Slack](https://docs.google.com/forms/d/e/1FAIpQLScsdTqssLrM9FinmpP8Mow2Hl8zJnfJZfjWxaeXddlvu2VjBw/viewform) channel.

**General Usage**

   This is a **_generalized_** specification representing only a **_minimum_** set of requirements for development of APIs to facilitate the transfer of archived web data between custodians, systems, repositories, end users, and others. This API focuses on the transfer of WARC and WARC-derived web data and aims to standardize vocabularies and features to inform those institutions, services, and developers building reference implementations local to their organizations. The basic purpose of this API is to return a results list of WARC files and derivative files originating from WARCs and corresponding essential metadata related to location/transfers in response to a user-defined query that includes implementation-specific parameters. The specification includes the notion of a "job" i.e. the ability to submit a job, receive a job token, and track a job status for the creation of derivative web data files that need to be generated locally and will be available via the API upon job completion. This allows the API to meet the intended goals of supporting both WARC file transfer for preservation replication as well as the ability to allow for derivative datasets to be delivered to researchers and users.

**Assumptions & Exclusions**

* Implementation APIs built using this specification should be RESTful.
* Implementation APIs should, at minimum, produce application/json.
* Implementation APIs must support GET and POST.
* This specification does not cover authentication and access control, which are considered to be institution and implementation specific.
* This specification abstracts away institution-specific details in many areas to remain generalizable and minimal. Additional paths, methods, and functions can be added in implementations as desired.
* The specification allows for both the return of results considered "complete" and “includes extra.” This allow requestors to know if the returned results fully meet the original query or whether addition data is contained in the file list returned. Details are below.

**Issues for General Discussion**

* The "transfer confirmation" functionality originally proposed by the development team was dropped. This functionality was intended to verify a successful transfer once the transfer was complete. It seemed too challenging to force every implementation to develop and support this as a bare minimum, as it could get technically complicated. Implementations can still build it in to their API. To facilitate the ability to confirm a transfer, checksum was made a required return value for **/webdata**.
* A true/false result for "includes-extra" will be part of all **/webdata** query returns to denote the “inclusive v. exclusive” issues discussed in design meetings.
* Some questions/decisions remained around whether a "filename" should match directories in a “full path,” and if so, how “\*” wildcard/globs should match directory separators, for instance, *\/webdata?filename=ARCHIVEIT-1234-2016\*.warc.gz.  For now, we suggest an implementation may support searching the full path only as an extension to the set of query parameters.
* There was debate around how APIs should define and document themselves. Originally idea was to have a **/registry** path under each main path that would return implementation specific information, such as parameters to **/webdata** and functions to **/jobs**. Alternately, the base path could simply return a Swagger YAML file that defines the full API. For discussion, and potentially can be an implementation detail. The WASAPI team will decide where this information lives and what is required of implementations (if anything).
* We should determine the right way of specifying compression along with the format of files.
* Are we offering too much flexibility with WebdataMenu and WebBundles and the multiple "locations" of a WebdataFile?  How frequently do implementations offer mirrored files vs offer multiple transport methods of the same webdata? What is the level of requirement for granularity here?

**Paths & Examples**

  * **/webdata**

   *(example: https://<i></i>partner.archive-it.org/v0/export/api/webdata)*

The most basic query using the **/webdata** path returns a list of all web data files on the server which are available to the client, basic metadata about those files, and their download information. Parameters to modify **/webdata** will be determined by institutions building their own implementations. Potential parameters can be as simple as */webdata?directoryName=[name]* or can support an extensive list of parameters to modify a request. Examples of possible parameters could include those defining identifiers for things like account, collection, seed, crawl job, harvest event, session, date range, archival identifier, administrative unit, repository, bucket, and more. All institution-specific query filters and modifiers should be parameters to the **/webdata** path.

   * **Example queries and results**

*https://<i></i>partner.archive-it.org/v0/export/api/webdata?filename=2016-08-30-blah.warc.gz*

The above query would return a list of a single WARC file (though it may be available via multiple transports).

```
{
    "includes-extra": false,
    "files": [
        {
            "checksum": "md5:b1c3cd...57; sha1:011c65...a7",
            "content-type": "application/warc",
            "filename": "2016-08-30-blah.warc.gz",
            "locations": [
                "http://archive-it.org/.../2016-08-30-blaugh.warc.gz",
                "gridftp globus://...",
                "ipfs/Qmbeef0484098..."
            ]
        }
    ]
}
```

*https://<i></i>partner.archive-it.org/v0/export/api/webdata?acccountId=123&collectionId=456&startDate=01012014&endDate=12312015*

The above query would return a list of all the WARCs (with metadata and download links) from between January 1, 2014 and December 31, 2015 for Account 123, Collection 456.

```
{
    "includes-extra": false,
    "files": [
        {
            "checksum": "md5:beefface09384509",
            "content-type": "application/warc",
            "filename": "2014-01-01-blah.warc.gz",
            "locations": [
                "http://archive-it.org/.../2014-01-01-blah.warc.gz",
                "/ipfs/Qmde62f92ea12c42dc0b0c0ab3952e52e1"
            ]
        },
        {
            "checksum": "md5:beefface09384510",
            "content-type": "application/warc",
            "filename": "2014-01-02-blah.warc.gz",
            "locations": [
                "http://archive.org/.../2014-01-02-blah.warc.gz",
                "/ipfs/Qmbda3f7abccdad41977fb308453566f84"
            ]
        }
    ]
}
```

  * **/jobs**

   *(example: https://<i></i>partner.archive-it.org/v0/export/api/jobs)*

The **/jobs** path shows the jobs on this server accessible to the client. This enables the request and deliver of WARC derivative webdata files. The **/jobs** path supports GET and POST methods. Implementations that do not include the ability to submit a job should still support his path and simply return that no jobs are possible for the client on this server.

   * **Example queries and results**

GET  *https://<i></i>partner.archive-it.org/v0/export/api/jobs*

Results here depend on whether jobs have been submitted. If no jobs have been submitted, you get an empty list. If you have submitted jobs, you get something similar to the below.

```
[
    {
        "jobtoken": "21EC2020-08002B30309D",
        "function": "build-wat",
        "query": "acccountId=123&collectionId=456&startDate=2014&endDate=2015",
        "submit-time": "2016-08-30Z15:52:53",
        "state": "complete",
        "result": [
            [
                {
                    "checksum": "md5:beefface09384509",
                    "content-type": "application/wat",
                    "filename": "2014-01-01-blah.wat.gz",
                    "locations": [
                        "http://archive-it.org/.../2014-01-01-blah.wat.gz"
                    ]
                },
                {
                    "checksum": "md5:beefface09384510",
                    "content-type": "application/wat",
                    "filename": "2014-01-02-blah.wat.gz",
                    "locations": [
                        "http://archive-it.org/.../2014-01-02-blah.wat.gz"
                    ]
                }
            ]
        ]
    }
]
```

POST *https://<i></i>partner.archive-it.org/v0/export/api/jobs*

The POST method includes a string matching a **/webdata** query string plus an implementation-specific function available to the client. In this specification, POST requests remain a bit of an abstraction, as they are dependent upon the implementation-specific parameters supported under **/webdata**.

Using the previous **/webdata** example, the below POST request would return a job token for creating WATs for WARC files matching that **/webdata** query:

 *https://<i></i>partner.archive-it.org/v0/export/api/jobs?acccountId=123&collectionId=456&startDate=2014&endDate=2015&function=build-wat*

```
{
    "jobtoken": "21EC2020-08002B30309D",
    "function": "build-wat",
    "query": "acccountId=123&collectionId=456&startDate=2014&endDate=2015",
    "submit-time": "2016-08-30Z15:52:53",
    "state": "queued"
}
```

  * **/jobs/{jobToken}**

   *(example: https://<i></i>partner.archive-it.org/v0/export/api/jobs/123456)*

The **/jobs/{jobToken}** path returns the status of a submitted job.

   * **Example queries and results**

GET *https://<i></i>partner.archive-it.org/v0/export/api/jobs/21EC2020-08002B30309D*

Retrieve status for a submitted job, some metadata, including the original query, time it was requested, etc. Includes results list if job is finished. Results are not necessarily available indefinitely. May return "410 Gone" if derivatives generated by this job have been replaced (e.g. by the results of a newer job), or if job has been expired by some other policy. An implementation may (but is not required to) make results later available under /webdata queries.

```
{
    "jobtoken": "21EC2020-08002B30309D",
    "function": "build-wat",
    "query": "acccountId=123&collectionId=456&startDate=2014&endDate=2015",
    "submit-time": "2016-08-30Z15:52:53",
    "state": "complete",
    "result": [
        [
            {
                "checksum": "md5:beefface09384509",
                "content-type": "application/wat",
                "filename": "2014-01-01-blah.wat.gz",
                "locations": [
                    "http://archive-it.org/.../2014-01-01-blah.wat.gz"
                ]
            },
            {
                "checksum": "md5:beefface09384510",
                "content-type": "application/wat",
                "filename": "2014-01-02-blah.wat.gz",
                "locations": [
                    "http://archive-it.org/.../2014-01-02-blah.wat.gz"
                ]
            }
        ]
    ]
}
```

**Additional Definitions**

The result of a /webdata query or result of a job can be represented in multiple formats and offered via multiple transports.  To express this and allow the client to select the most appropriate, an implementation includes a "WebdataMenu" in each result.  A WebdataMenu offers a number of “WebdataBundles”, each of which provide the complete result with a distinct format and transport.  Each WebdataBundle contains one or more WebdataFiles.  The client chooses a WebdataBundle with appropriate format and transport.

Here’s an example of a single WebdataMenu which contains two WebdataBundles.  The first WebdataBundle contains three WebdataFiles; the second contains one.

```
[
 [  ‘http://partner.archive-it.org/.../2016-08-30-blah.warc.gz’,
    ‘http://partner.archive-it.org/.../2016-08-30-blah1.warc.gz’,
    ‘http://partner.archive-it.org/.../2016-08-30-blah2.warc.gz’
 ],
 [  ‘ipfs/Qm67e26534d15bc305340ce4b2e5944ffc’ ]
]
```

**Timeline & Contacts**

This document and the accompanying Swagger .yaml file was shared across the primary development project team for comment and input in early September 2016. The document will be shared in late September with the full grant team, Technical Working Group, and program managers and engineers of the web archiving community attending the IIPC Steering Committee meeting and Crawler Hackathon at British Library the week of September 19, 2016. After a period of comments, the spec and doc will be shared with the full web archiving community for additional feedback. Reference implementations of the specification will be developed by Internet Archive (Archive-It) and Stanford (LOCKSS) in Q4 of 2016. Testing, iterative development, and other ongoing activities will take place in 2017.

*Internet Archive (Archive-It)*
* Jefferson Bailey, Director, Web Archiving, jefferson@archive.org
* Mark Sullivan, Web Archiving Software Engineer, msullivan@archive.org

*Stanford University Libraries (DLSS & LOCKSS)*
* Nicholas Taylor, Web Archiving Service Manager, ntay@stanford.edu
* David Rosenthal, LOCKSS Chief Information Scientist, dshr@standford.edu
