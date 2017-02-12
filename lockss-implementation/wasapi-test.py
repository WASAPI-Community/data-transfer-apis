#!/usr/bin/env python3

# A minimal client for the WASAPI transfer API, with
# defaults matching the LOCKSS implementation
#
# Arguments:
# -f [function] or --function [function] default auid
# -q [query] or --query [query] default AUID for SimulatedContent

from argparse import ArgumentParser
import requests
import json

# URL prefix for WSAPI service
service = "http://localhost:8080/v0"
testAUID = 'org|lockss|plugin|simulated|SimulatedPlugin&root~%2Ftmp%2F'
err = "Error: "

# Return a Dictionary with the params for the WSAPI request
def makeWsapiParams():
	parser = ArgumentParser()
	parser.add_argument("-f", "--function", dest="myFunction", help="WASAPI function", default="auid")
	parser.add_argument("-q", "--query", dest="myQuery", default=testAUID, help="WASAPI query")
	args = parser.parse_args()
	ret = None
	if (args.myQuery != None and args.myFunction != None):
		ret = {}
		ret['query'] = args.myQuery
		ret['function'] = args.myFunction
	return ret

params1 = makeWsapiParams()
if params1 != None:
	# query the service
	wasapiResponse = requests.post(service + "/jobs", data=params1)
	status = wasapiResponse.status_code
	if(status == 200):
		# WASAPI request successful
		err = ""
		# parse the JSON we got back
		wasapiData = wasapiResponse.json()
		message = json.dumps(wasapiData)
	else:
		# WASAPI request unsuccessful
		message = "WSAPI request error: {0}\n{1}".format(status,wasapiResponse)
else:
	message = "Usage: wasapi-test -q [query] -f [function]"
print('WASAPI test')
print("{0}{1}".format(err,message))
print()
