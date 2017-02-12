#!/usr/bin/env python3
import os, sys
import suds
from suds.client import Client
import json
from datetime import datetime, timezone
from base64 import b64decode
import hashlib

persistentFile = '/tmp/wsapiJobs'
testAUID = 'org|lockss|plugin|simulated|SimulatedPlugin&root~%2Ftmp%2F'
# LOCKSS SOAP export web service
# NB - org.lockss.export.enabled=true must be set when the daemon starts
# for the returned URL to be valid.
# XXX these should be arguments
host = 'localhost:8081'
url = 'http://'+host+'/ws/ExportService?wsdl'
user = 'lockss-u'
pwd4lockss = 'lockss-p'

# WSAPI API
def jobs_post(query = None, function = None, parameters = None) -> str:
	# WARC creation is supposed to be asynchronous, but for now we
	# make it synchonous, so all jobs are in status 'complete'
	if function != 'auid':
		return ""
	# XXX for now, query is simply an AUID
	# XXX query should be a list of AUIDs, not just one
	client = Client(url, username=user, password=pwd4lockss)
	params = makeParams(client, query)
	results = client.service.createExportFiles(params)
	jobId = makeJobId()
	putJob(jobId, params, results)
	return makePostResponse(jobId, params, encodeResults(results))

def webdata_get(filename = None, contentType = None) -> str:
	# XXX webdata requires that content be returned selectively
	# XXX if it matches specified URL globbing and/or mime type.
	# The LOCKSS daemon's SOAP-y API does not support this.
	message = {
		'status': '400',
		'message': 'Content filtering not supported'
	}
	resp = jsonify(message)
	resp.status_code = 400
	return resp

def jobs_get() -> str:
	ret = {}
	jobs = getJobs()
	ret = json.dumps(jobs)
	return ret

def jobs_job_token_get(jobToken) -> str:
	ret = []
	job = getJob(jobToken)
	if job != None:
		params = job['params']
		ret['function'] = params['function']
		ret['jobtoken'] = jobToken
		ret['query'] = params['query']
		ret['state'] = 'complete'
		ret['submit-time'] = jobs['submit-time']
	return json.dumps(ret)

# Persistent state - i.e. jobs database
def putJob(jobId, params, results = None):
	ret = None
	state = {'params':encodeParams(params),
		'results':encodeResults(results),
		'submit-time':encodeTime()}
	try:
		fileState = os.stat(persistentFile)
	except FileNotFoundError as ex:
		jobs = {}
	else:
		if fileState.st_size > 0:
			with open(persistentFile, 'r') as f:
				jobs = json.load(f)
		else:
			jobs = {}
	with open(persistentFile, 'w') as f:
		jobs[jobId] = state
		json.dump(jobs, f)
		ret = jobId
	return ret

def getJob(jobId):
	try:
		with open(persistentFile, 'r') as f:
			# XXX need to lock file
			jobs = json.load(f)
			return jobs[jobId]
	except FileNotFoundError:
		return None
def getJobs():
	try:
		with open(persistentFile, 'r') as f:
			# XXX need to lock file
			jobs = json.load(f)
			return jobs
	except FileNotFoundError:
		return []

# LOCKSS SOAP-y export web service
def makeParams(client, auid):
	typeEnum = client.factory.create(u'typeEnum')
	filenameTranslationEnum = client.factory.create(u'filenameTranslationEnum')
	params = client.factory.create(u'exportServiceParams')
	params.auid = auid
	params.compress = 1
	params.excludeDirNodes = 0
	params.fileType = typeEnum.WARC_RESOURCE
	params.filePrefix = 'lockss-export-'
	params.maxSize = -1
	params.maxVersions = -1
	params.xlateFilenames = filenameTranslationEnum.XLATE_NONE
	return params

# Encode exportServiceParams as a Dictionary
def encodeParams(params):
	ret = {}
	ret['auid'] = params.auid
	ret['compress'] = params.compress
	ret['excludeDirNodes'] = params.excludeDirNodes
	ret['fileType'] = params.fileType
	ret['filePrefix'] = params.filePrefix
	ret['maxSize'] = params.maxSize
	ret['maxVersions'] = params.maxVersions
	ret['xlateFilenames'] = params.xlateFilenames
	return ret

# Encode exportServiceWsResult as Dictionary
# XXX there is currently no option to the SOAP-y API to select
# XXX between streaming the WARC and placing it in the export
# XXX directory - it does both.
def encodeResults(results):
	ret = {}
	ret['auid'] = results.auId
	ret['name'] = results.dataHandlerWrappers[0].name
	ret['size'] = results.dataHandlerWrappers[0].size
	# XXX we need the LOCKSS daemon to compute the
	# XXX checksum of the files it puts in the export
	# XXX directory so that exports can be validated.
	# XXX We would fetch the checksum file here to get
	# XXX the checksum.
	# XXX Instead we compute the checksum of the streamed
	# XXX WARC content but this isn't an end-to-end check.
	b = bytes(results.dataHandlerWrappers[0].dataHandler, "utf-8")
	warc = b64decode(b)
	m = hashlib.sha1()
	m.update(warc)
	ret['sha1'] = m.hexdigest()
	return ret

def encodeTime():
	local_time = datetime.now(timezone.utc).astimezone()
	return local_time.isoformat()

def makeJobId():
	# XXX for now, jobId is submission time
	return encodeTime()

# Return the body of the POST response
def makePostResponse(jobId, params, results):
	ret = {
		"includes-extras":False,
		"files":[
			{
				"checksum":"sha1:" + results['sha1'],
				"content-type":"application/warc",
				"filename":results['name'],
				"locations":[
					"http://"+host+"/export/"+results['name']
				],
				"size":results['size']
			}
		]
	}
	return json.dumps(ret)
