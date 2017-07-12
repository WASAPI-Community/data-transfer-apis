from __future__ import absolute_import
from django.core.urlresolvers import reverse
from django.db import models
from .mailer import new_wasapijob
from django.db.models.signals import post_save
from archiveit.archiveit.model_fields import AitWasapiDateTimeField

class WasapiJob(models.Model):

    id = models.AutoField(primary_key=True)

    # fields for minimal, generic WASAPI:

    # This list of functions is specific to Archive-It:
    FUNCTIONS = [
      # (identifier, code,         english)
      ("BUILD_WAT",  "build-wat",  "Build a WAT file"),
      ("BUILD_WANE", "build-wane", "Build a WANE file"),
      ("BUILD_CDX",  "build-cdx",  "Build a CDX file")]
    for identifier, code, english in FUNCTIONS:
        locals()[identifier] = code
    FUNCTION_CHOICES = [(code, english) for identifier, code, english in FUNCTIONS]
    function = models.CharField(max_length=32, null=False, choices=FUNCTION_CHOICES)

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

    class Meta:
        managed = False
        db_table = 'WasapiJob'

    def __str__(self):
        return "<WasapiJob %s in state %s>" % (self.id, self.state)

    def get_absolute_url(self):
        return reverse('wasapijob-detail', kwargs={'pk':self.id})


# Voodoo to patch bug exposed in restore_object:
# TypeError: can only concatenate tuple (not "list") to tuple
# at ait5/ lib/python3.5/site-packages/rest_framework/serializers.py:969
# for field in meta.many_to_many + meta.virtual_fields:
WasapiJob._meta.virtual_fields = ()  # was []; many_to_many is ()

post_save.connect(receiver=new_wasapijob, sender=WasapiJob)
