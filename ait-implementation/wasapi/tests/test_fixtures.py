from django.test import TestCase

from archiveit.archiveit.models import CrawlJob, WarcFile

class TestFixtures(TestCase):
    '''Ensure we have the set of fixtures other tests depend on'''
    fixtures = ['archiveit/wasapi/tests/fixtures.json']

    def test_nested_sets_of_warcfiles(self):
        '''To test an automatically built query, we need some WarcFiles that
        match it and some that don't match it'''
        # the interesting WarcFile at the core of the nested sets
        awarc = WarcFile.objects.get(id=1)
        self.assertGreater(
          len(WarcFile.objects.filter(crawl_job_id=awarc.crawl_job_id)),
          1,
          "Should have multiple WarcFiles in the crawl job")
        self.assertGreater(
          len(WarcFile.objects.filter(collection_id=awarc.collection_id)),
          len(WarcFile.objects.filter(crawl_job_id=awarc.crawl_job_id)),
          "Should have WarcFiles in the collection outside the crawl job")
        self.assertGreater(
          len(WarcFile.objects.filter(account_id=awarc.account_id)),
          len(WarcFile.objects.filter(collection_id=awarc.collection_id)),
          "Should have WarcFiles in the account outside the collection")
        self.assertGreater(
          len(WarcFile.objects.all()),
          len(WarcFile.objects.filter(account_id=awarc.account_id)),
          "Should have WarcFiles outside the account")

    def test_fields_of_warcfiles_are_unique(self):
        for fieldname in ['filename','md5','sha1']:
            self.assertEqual(
              conflicts(WarcFile.objects.all(), fieldname), {},
              "%s values should be unique across WarcFiles" % (fieldname))

    def test_denormalization(self):
        self.assertEqual(
          [warcfile for warcfile in WarcFile.objects.all()
            if warcfile.crawl_job and
              warcfile.collection_id != warcfile.crawl_job.collection_id],
          [],
          "each warcfile should match its crawl job's collection")
        self.assertEqual(
          [warcfile for warcfile in WarcFile.objects.all()
            if warcfile.crawl_job and
              warcfile.account_id != warcfile.crawl_job.account_id],
          [],
          "each warcfile should match its crawl job's account")
        self.assertEqual(
          [crawl_job for crawl_job in CrawlJob.objects.all()
            if crawl_job.collection.account_id != crawl_job.account_id],
          [],
          "each crawl job should match its collection's account")


def conflicts(col, fieldname):
    '''Returns a dict of lists of conflicting elements keyed by their elements' value from partition_key'''
    partition_key = lambda obj: obj.__getattribute__(fieldname)
    return dict(
      [k,v] for k,v in partition(col, partition_key, list).items()
      if len(v) > 1 )

def partition(col, partition_key, empty_col=None):
    '''Returns a dict to the set of elements keyed by their value from partition_key'''
    if empty_col == None:
        empty_col = type(col)
    ret = {}
    for item in col:
        key = partition_key(item)
        ret[key] = ret.get(key, empty_col())
        ret[key].append(item)
    return ret
