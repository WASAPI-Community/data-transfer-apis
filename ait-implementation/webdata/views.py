import re
from subprocess import Popen, PIPE
from django.shortcuts import render
from django.http import HttpResponse, FileResponse
from django.conf import settings

from internetarchive import get_session

from archiveit.archiveit.models import WarcFile

VERBOTEN_FILENAMES = re.compile(r'EXTRACTED|EXTRACTION|HISTORICAL')

def index(request, filename):

    # check authorization:
    if request.user.is_anonymous():
        # TODO:  rfc7235#section-4.1 says to include WWW-Authenticate header
        return HttpResponse('You are not authenticated; please log in to download the requested file: %s'%filename,
          content_type='text/plain', status=401)
    match = re.search(r'^(?:ARCHIVEIT-)?(\d+)-', filename)
    if not match:
        return HttpResponse(
          'Failed to parse collection id from requested filename: %s'%filename,
          content_type='text/plain', status=404)
    file_collection_id = int(match.group(1))
    if(VERBOTEN_FILENAMES.match(filename) or
      not may_access_collection_id(request, file_collection_id)):
        return HttpResponse(
          'You are not authorized to download the requested file: %s'%filename,
          content_type='text/plain', status=403)

    # fetch the file's db record:
    warcfile = WarcFile.objects.filter(filename=filename).first()
    if not warcfile:
        return HttpResponse('404 Not Found',
          content_type='text/plain', status=404)

    # get the file's content from somewhere:
    stream = (
      warcfile.pbox_item and
        stream_from_pbox(warcfile.pbox_item, filename) or
      warcfile.hdfs_path and
        stream_from_hdfs(warcfile.hdfs_path, filename) )
    if not stream:
      return HttpResponse("500 Can't fetch file",
        content_type='text/plain', status=500)

    # give it all back to the client:
    response = FileResponse(stream)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Length'] = warcfile.size
    return response

def stream_from_pbox(itemname, filename):
    # TODO:  handle errors etc
    archive_session = get_session(config_file=settings.IATOOL_CONFIG_PATH)
    item = archive_session.get_item(itemname)
    files = item.get_files(filename)
    file = files.__next__()
    return file.download(return_responses=True)

def stream_from_hdfs(hdfs_path, filename):
    # TODO:  consider using python3 snakebite
    # TODO:  handle errors etc; would be nice to examine returncode
    # (but halfway through a big stream is too late to tell the client, right?)
    hdfs_cat = Popen([settings.HDFS_EXE, 'dfs', '-cat', hdfs_path],
      env=settings.HADOOP_ENV, stdout=PIPE)
    return hdfs_cat.stdout

def may_access_collection_id(request, collection_id):
    if request.user.is_superuser:
        return True
    return collection_id in request.user.account.collection_set.values_list('id', flat=True)
