from __future__ import absolute_import
from datetime import datetime
import re
from django.core.urlresolvers import reverse
from django.db import models
from .mailer import new_wasapijob, complete_wasapijob
from django.db.models.signals import post_save, pre_save
from django.http import QueryDict
from archiveit.archiveit.models import WarcFile, DerivativeFile
from archiveit.archiveit.model_fields import AitWasapiDateTimeField
from archiveit.wasapi.selectors import select_webdata_query


# This set of functions is specific to Archive-It:
function_instances = {}
class JobFunction(object):
    identifier = None
    code       = None
    english    = None
    @staticmethod
    def ideal_results_for(job, source_files):
        '''Transform DerivativeFile records to new WasapiJobResultFile
        records according to the job function'''
        assert NotImplementedError('Implement in concrete class')

    @classmethod
    def register(cls):
        assert cls.identifier not in function_instances, "Already got one"
        function_instances[cls.code] = cls

class BuildWat(JobFunction):
    identifier = "BUILD_WAT"
    code       = "build-wat"
    english    = "Build a WAT file"
    @staticmethod
    def ideal_results_for(job, source_files):
        return [WasapiJobResultFile(
          job=job,
          filename=re.sub(r'\.(w?arc)\.gz', '_\\1.wat.gz', warcfile.filename)
        ) for warcfile in source_files]
BuildWat.register()

class BuildWane(JobFunction):
    identifier = "BUILD_WANE"
    code       = "build-wane"
    english    = "Build a WANE file"
    @staticmethod
    def ideal_results_for(job, source_files):
        return [WasapiJobResultFile(
          job=job,
          filename=re.sub(r'\.(w?arc)\.gz', '_\\1.wane.gz', warcfile.filename)
        ) for warcfile in source_files]
BuildWane.register()

class BuildCdx(JobFunction):
    identifier = "BUILD_CDX"
    code       = "build-cdx"
    english    = "Build a CDX file"
    @staticmethod
    def ideal_results_for(job, source_files):
        return [WasapiJobResultFile(
          job=job,
          filename=re.sub(r'\.(w?arc)\.gz', '_\\1.cdx.gz', warcfile.filename)  # TODO:  wait to support CDX
        ) for warcfile in source_files]
#BuildCdx.register()  # TODO:  implement and register

class BuildLga(JobFunction):
    identifier = "BUILD_LGA"
    code       = "build-lga"
    english    = "Build an LGA file"
    @staticmethod
    def ideal_results_for(job, source_files):
        # TODO:  we ignore the results of the query, so don't execute it
        # note lack of list comprehension (because LGA is not one-to-one)
        return [WasapiJobResultFile(
          job=job,
          filename='ARCHIVEIT-%d-LONGITUDINAL-GRAPH-%4d-%02d-%02d.lga.tgz' % (
            job.collection,  # TODO:  but jobs are too general, pull from query?
            job.submitTime.year, job.submitTime.month, job.submitTime.day)
        )]
#BuildLga.register()  # TODO:  implement and register


class WasapiJob(models.Model):

    id = models.AutoField(primary_key=True)

    # fields for minimal, generic WASAPI:

    FUNCTION_CHOICES = [(concrete_instance.code, concrete_instance.english)
      for concrete_instance in function_instances.values()]
    function = models.CharField(max_length=32, null=False, choices=FUNCTION_CHOICES)
    @property
    def function_instance(self):
        return function_instances[self.function]

    query = models.CharField(max_length=1024, blank=True, null=False)
    submit_time = AitWasapiDateTimeField(db_column='submitTime', auto_now_add=True, null=False)
    termination_time = AitWasapiDateTimeField(db_column='terminationTime', null=True, blank=True)

    # This list of states is specific to Archive-It:
    STATES = [
      # (identifier, code,       english)
      ("QUEUED",     "queued",   "Queued"),
      ("RUNNING",    "running",  "Running"),
      ("FAILED",     "failed",   "Failed"),
      ("COMPLETE",   "complete", "Complete"),
      ("GONE",       "gone",     "Gone")]
    for identifier, code, english in STATES:
        locals()[identifier] = code
    STATE_CHOICES = [(code, english) for identifier, code, english in STATES]
    state = models.CharField(max_length=32, null=False, choices=STATE_CHOICES)

    # fields specific to Archive-It:

    account = models.ForeignKey('accounts.Account', db_column='accountId', editable=False, blank=True)
    user = models.ForeignKey('accounts.User', db_column='userId', editable=False, blank=True)

    class Meta:
        managed = False
        db_table = 'WasapiJob'

    # the same as WebdataQueryViewSet
    queryset = WarcFile.objects.all().order_by('-id')
    def query_just_like_webdataqueryviewset(self):
        '''Create the same queryset that WebdataQueryViewSet executes'''
        querydict = QueryDict(self.query)
        return select_webdata_query(querydict, self.queryset,
          account=self.account, user=self.user)

    def set_ideal_result_and_state(self, source_files):
        '''Calculate WasapiJobResultFiles that would comprise result when
        complete; update state'''
        ideal_results = self.function_instance.ideal_results_for(self, source_files)
        # TODO:  batch the DB query
        for ideal_result in ideal_results:
            ideal_result.update_state()
        if all(ideal_result.is_complete() for ideal_result in ideal_results):
            # vacuous (if ideal_results is empty) or freebie job
            self.state = self.COMPLETE
            self.termination_time = datetime.now()
            # new_wasapijob will say complete so needn't call complete_wasapijob
            self._ideal_results = []
        else:
            # juicy job, ie have to do some work
            self.state = self.QUEUED
            self._ideal_results = ideal_results  # save them after we get our id

    def save_results(self):
        '''Save the WasapiJobResultFile records now that they can refer to
        their WasapiJob record'''
        for ideal_result in self._ideal_results:
            ideal_result.job = self  # job_id wasn't yet available at creation
            ideal_result.save()

    def update_state(self):
        if self.state in (self.RUNNING, self.QUEUED):
            ideal_results = WasapiJobResultFile.objects.filter(job=self)
            if all(ideal_result.is_complete() for ideal_result in ideal_results):
                self.state = self.COMPLETE
                self.termination_time = datetime.now()
                complete_wasapijob(self)

    def __str__(self):
        return "<WasapiJob %s in state %s>" % (self.id, self.state)

    def get_absolute_url(self):
        return reverse('wasapijob-detail', kwargs={'pk':self.id})

    @staticmethod
    def covering_collection_times(source_files):
        '''Returns a list of (collection,start,end) tuples.  Deriving each
        collection for the given time range will generate a superset of the
        desired result files.'''
        by_collection = {}
        for source_file in source_files:
            partition = by_collection.get(source_file.collection, set())
            by_collection[source_file.collection] = partition
            partition.add(source_file)
        return [
          ( collection,
            min(sf.crawl_time for sf in sfs),
            max(sf.crawl_time for sf in sfs) )
          for collection, sfs in by_collection.items()]

    @classmethod
    def pre_save(cls, instance, **kwargs):
        job = instance
        if not job.id:  # freshly created job
            source_files = job.query_just_like_webdataqueryviewset()
            job.set_ideal_result_and_state(source_files)
            job._source_files = source_files  # stash for mailer in post-save

    @classmethod
    def post_save(cls, instance, **kwargs):
        # would prefer to call the parameter "job", but "send" passes it by name
        job = instance
        if hasattr(job, '_source_files'):  # freshly created job
            job.save_results()
            new_wasapijob(job, cls.covering_collection_times(job._source_files))

pre_save.connect(receiver=WasapiJob.pre_save, sender=WasapiJob)
post_save.connect(receiver=WasapiJob.post_save, sender=WasapiJob)

# Voodoo to patch bug exposed in restore_object:
# TypeError: can only concatenate tuple (not "list") to tuple
# at ait5/ lib/python3.5/site-packages/rest_framework/serializers.py:969
# for field in meta.many_to_many + meta.virtual_fields:
WasapiJob._meta.virtual_fields = ()  # was []; many_to_many is ()


def proxy_to_derivative(*fields):
    def decorator(cls):
        # invoke another method to prevent iterator variable from varying
        def install_proxy(cls, field):
            @property
            def ameth(self):
                return( self.derivative_file and
                  getattr(self.derivative_file, field) )
            setattr(cls, field, ameth)
        for field in fields:
            install_proxy(cls, field)
        return cls
    return decorator

@proxy_to_derivative('filetype', 'md5', 'sha1', 'size', 'store_time',
  'crawl_time', 'account_id', 'collection_id', 'crawl_job', 'crawl_job_id',
  'pbox_item', 'hdfs_path')
class WasapiJobResultFile(models.Model):
    id = models.AutoField(primary_key=True)
    job = models.ForeignKey('WasapiJob', db_column='jobId')
    filename = models.CharField(max_length=4000)
    derivative_file = models.ForeignKey('archiveit.DerivativeFile', db_column='derivativeFileId', null=True)

    class Meta:
        managed = False
        db_table = 'WasapiJobResultFile'

    def is_complete(self):
        return self.derivative_file

    def update_state(self):
        '''Update reference to any newly existing derivative_file; return
        whether state changed (ie whether need to propagate changes further)'''
        if self.derivative_file:
            return False
        self.derivative_file = DerivativeFile.objects.filter(filename=self.filename).first()
        return self.derivative_file

    def dict_for_location(self):
        '''Return a mapping that can fill location templates'''
        d = self.__dict__
        d.update(pbox_item=self.pbox_item)
        return d

    def __repr__(self):
        return( 'WasapiJobResultFile(id=%s,filename=%s,job_id=%s,%s)' %
          (self.id, self.filename, self.job_id,
            "complete" if self.derivative_file else "incomplete"))

    @classmethod
    def update_completed_result_files(cls):
        '''Find and update result files that completed without notification'''
        result_files = cls.objects.raw('''
          select WasapiJobResultFile.id, WasapiJobResultFile.jobId
          from WasapiJobResultFile
          join DerivativeFile
            on WasapiJobResultFile.filename=DerivativeFile.filename
          where WasapiJobResultFile.derivativeFileId is null''')
        # TODO:  use that result rather than refetching for each result file
        cls.update_states(result_files)

    @staticmethod
    def update_states(result_files):
        jobs_to_update = set()
        for result_file in result_files:
            if result_file.update_state():
                result_file.save()
                jobs_to_update.add(result_file.job)
        # TODO:  batch the DB queries
        for job in jobs_to_update:
            job.update_state()
            job.save()
