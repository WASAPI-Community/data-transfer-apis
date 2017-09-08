from django.test import TestCase

from archiveit.accounts.models import Account, User
from archiveit.archiveit.models import Collection, CrawlJob, DerivativeFile
from archiveit.wasapi.models import WasapiJob, WasapiJobResultFile
from archiveit.wasapi.views import WebdataQueryViewSet

class TestJobResult(TestCase):
    fixtures = ['archiveit/wasapi/tests/fixtures.json']

    def test_query_execution(self):
        cases = [
          ('crawl=2',      {1,2},     "Query by crawl job"),
          ('collection=2', {1,2,3},   "Query by collection"),
          ('',             {1,2,3,4}, "Empty query ie query by account"),
        ]
        for query, ideal, msg in cases:
            with self.subTest(query=query):
                source_files = WasapiJob(
                  query=query,
                  account=Account.objects.get(id=1),
                  user=User.objects.get(username='authuser'),
                ).query_just_like_webdataqueryviewset()
                self.assertEqual(set(wf.id for wf in source_files), ideal, msg)

    def test_creation_of_resultfiles(self):
        job = WasapiJob(
          query='collection=2',
          function='build-wat',
          account=Account.objects.get(id=1),
          user=User.objects.get(username='authuser'))
        job.save()
        result_files = WasapiJobResultFile.objects.filter(job_id=job.id)
        ideal = {
          "ARCHIVEIT-2-CRAWL_SELECTED_SEEDS-JOB2-20140710003544123-00000_warc.wat.gz",
          "ARCHIVEIT-2-CRAWL_SELECTED_SEEDS-JOB2-20140710014044456-00000_warc.wat.gz",
          "ARCHIVEIT-2-CRAWL_SELECTED_SEEDS-JOB1-20140710014044455-00000_warc.wat.gz"}
        self.assertEqual( set(f.filename for f in result_files), ideal,
          "Create result files")

    def test_vacuous_job_should_update_its_own_state(self):
        '''"Vacuous" means the job needs no result files'''
        # partner creates job via DRF
        job = WasapiJob(
          query="filename=nonesuch",
          function='build-wat',
          account=Account.objects.get(id=1),
          user=User.objects.get(username='authuser'),
        )
        job.save()  # DRF calls save
        self.assertEqual(job.state, WasapiJob.COMPLETE,
          "Vacuous job should be in state complete after save")
        self.assertIsNotNone(job.termination_time,
          "Vacuous job should have a termination time after save")

    def test_freebie_job_should_update_its_own_state(self):
        '''"Freebie" means the job is satisfied by pre-existing result files'''
        account = Account.objects.get(id=1)
        user = User.objects.get(username='authuser')
        collection = Collection.objects.get(id=2)
        # some earlier job derives some files
        earlier_job = WasapiJob(function='build-wat',account=account,user=user)
        earlier_job.save()
        already_deriveds = [
          "ARCHIVEIT-2-CRAWL_SELECTED_SEEDS-JOB2-20140710003544123-00000",
          "ARCHIVEIT-2-CRAWL_SELECTED_SEEDS-JOB2-20140710014044456-00000",
          "ARCHIVEIT-2-CRAWL_SELECTED_SEEDS-JOB1-20140710014044455-00000",
        ]
        for rootname in already_deriveds:
            filename = rootname + '_warc.wat.gz'
            df = DerivativeFile(filename=filename,
              size=1, account=account, collection=collection)
            df.save()
            rf = WasapiJobResultFile(filename=filename,
              derivative_file=df, job=earlier_job)
            rf.save()
        # partner creates job via DRF
        job = WasapiJob(
          query='collection=%d' % (collection.id),
          function='build-wat',
          account=account,
          user=user)
        job.save()  # DRF calls save
        self.assertEqual(job.state, WasapiJob.COMPLETE,
          "Freebie job should be in state complete after save")
        self.assertIsNotNone(job.termination_time,
          "Freebie job should have a termination time after save")

    def test_juicy_job_should_update_state_upon_derive(self):
        '''"Juicy" means the job needs fresh result files'''
        account = Account.objects.get(id=1)
        user = User.objects.get(username='authuser')
        collection = Collection.objects.get(id=2)
        # partner creates job via DRF
        job = WasapiJob(
          query='collection=%d' % (collection.id),
          function='build-wat',
          account=account,
          user=user,
        )
        job.save()  # DRF calls save
        self.assertEqual(job.state, WasapiJob.QUEUED,
          "Juicy job should remain in state queued after save")
        self.assertIsNone(job.termination_time,
          "Juicy job should not have a termination time after save")

        # archivist manually changes its state
        job.state = WasapiJob.RUNNING
        job.save()
        self.assertEqual(job.state, WasapiJob.RUNNING,
          "Juicy job runs")

        # the first file is derived
        first_rf = WasapiJobResultFile.objects.get(filename='ARCHIVEIT-2-CRAWL_SELECTED_SEEDS-JOB2-20140710003544123-00000_warc.wat.gz')
        first_df = DerivativeFile(
          filename='ARCHIVEIT-2-CRAWL_SELECTED_SEEDS-JOB2-20140710003544123-00000_warc.wat.gz',
          size=1, account=account, collection=collection)
        first_df.save()
        # script notifies us of first derivative
        WasapiJobResultFile.update_states(WasapiJobResultFile.objects.filter(filename='ARCHIVEIT-2-CRAWL_SELECTED_SEEDS-JOB2-20140710003544123-00000_warc.wat.gz'))
        self.assertEqual(job.state, WasapiJob.RUNNING,
          "Juicy job should remain in state running during derivation")
        self.assertIsNone(job.termination_time,
          "Juicy job should not have a termination time during derivation")

        # the other files are derived
        other_basenames = [
          "ARCHIVEIT-2-CRAWL_SELECTED_SEEDS-JOB2-20140710014044456-00000",
          "ARCHIVEIT-2-CRAWL_SELECTED_SEEDS-JOB1-20140710014044455-00000",
        ]
        for basename in other_basenames:
            other_rf = WasapiJobResultFile.objects.get(
              filename=basename+'_warc.wat.gz')
            other_df = DerivativeFile(filename=basename+'_warc.wat.gz',
              size=1, account=account, collection=collection)
            other_df.save()
        # script notifies us of other derivatives
        for basename in other_basenames:
            WasapiJobResultFile.update_states(WasapiJobResultFile.objects.filter(filename=basename+'_warc.wat.gz'))
        job.refresh_from_db()
        self.assertEqual(job.state, WasapiJob.COMPLETE,
          "Juicy job should change to state completed when files derived")
        self.assertIsNotNone(job.termination_time,
          "Juicy job should get a termination time when files derived")

    def test_juicy_job_should_update_state_upon_cron(self):
        '''"Juicy" means the job needs fresh result files'''
        account = Account.objects.get(id=1)
        user = User.objects.get(username='authuser')
        collection = Collection.objects.get(id=2)
        # partner creates job via DRF
        job = WasapiJob(
          query='collection=%d' % (collection.id),
          function='build-wat',
          account=account,
          user=user)
        job.save()  # DRF calls save
        self.assertEqual(job.state, WasapiJob.QUEUED,
          "Juicy job should remain in state queued after save")
        self.assertIsNone(job.termination_time,
          "Juicy job should not have a termination time after save")

        # archivist manually changes its state
        job.state = WasapiJob.RUNNING
        job.save()
        self.assertEqual(job.state, WasapiJob.RUNNING,
          "Juicy job runs")

        # the files are derived
        other_basenames = [
          "ARCHIVEIT-2-CRAWL_SELECTED_SEEDS-JOB2-20140710003544123-00000",
          "ARCHIVEIT-2-CRAWL_SELECTED_SEEDS-JOB2-20140710014044456-00000",
          "ARCHIVEIT-2-CRAWL_SELECTED_SEEDS-JOB1-20140710014044455-00000",
        ]
        for basename in other_basenames:
            other_rf = WasapiJobResultFile.objects.get(
              filename=basename+'_warc.wat.gz')
            other_df = DerivativeFile(filename=basename+'_warc.wat.gz',
              size=1, account=account, collection=collection)
            other_df.save()
        # but the script somehow doesn't notify us of other derivatives
        self.assertEqual(job.state, WasapiJob.RUNNING,
          "Juicy job should remain in state running without notification")
        self.assertIsNone(job.termination_time,
          "Juicy job should remain without a termination time without notification")
        # cronjob triggers clean up
        WasapiJobResultFile.update_completed_result_files()
        job.refresh_from_db()
        self.assertEqual(job.state, WasapiJob.COMPLETE,
          "Juicy job should change to state completed after clean up")
        self.assertIsNotNone(job.termination_time,
          "Juicy job should get a termination time after clean up")
