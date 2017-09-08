from django.conf import settings
from django.core.mail import send_mail

def new_wasapijob(job, covering_collection_times):
    message_template = """
Dear Web Archivists,

{user_full_name:s} of account "{account_name:s}" ({account_id:d}) has submitted a new job ({job_id:d}):
{function:s}
{query:s}

{urls:s}

{todo}

Love,
WASAPI within AIT5
"""
    if not covering_collection_times:
        todo = "The query matched no files, so the job is already complete."
    elif job.state == job.COMPLETE:
        todo = "The query matched only files already derived, so the job is already complete."
    else:
        todo = (
          "Please derive from these collections over these time spans:\n" +
          "\n".join([
            '%s %s %d %s %s' % (start, end, collection.id,
              collection.account.organization_name, collection.name)
            for collection,start,end in covering_collection_times ]))
    message = message_template.format(
      user_full_name = job.user.full_name,
      account_name = job.account.organization_name,
      account_id = job.account.id,
      job_id = job.id,
      function = job.function,
      query = job.query,
      urls = '\n'.join(
        [settings.BASE50URL + job.get_absolute_url()] +
        ([settings.BASE50URL + job.get_absolute_url() + '/result']
          if job.state==job.COMPLETE else []) +
        ['%s/admin/wasapi/wasapijob/%d/' % (settings.BASE50URL, job.id)] ),
      todo = todo,
    )
    send_mail(
      'Research Services Dataset Request via WASAPI',
      message,
      'donotreply@archive-it.org',
      settings.AITRESEARCHSERVICES_ADDRESS,
      fail_silently=False)


def complete_wasapijob(job):
    message_template = """
Dear Web Archivists,

The job ({job_id:d}) for {user_full_name:s} of account "{account_name:s}" ({account_id:d}) has completed:
{function:s}
{query:s}

{urls:s}

Love,
WASAPI within AIT5
"""
    message = message_template.format(
      user_full_name = job.user.full_name,
      account_name = job.account.organization_name,
      account_id = job.account.id,
      job_id = job.id,
      function = job.function,
      query = job.query,
      urls = '\n'.join([
        settings.BASE50URL + job.get_absolute_url(),
        settings.BASE50URL + job.get_absolute_url() + '/result',
        '%s/admin/wasapi/wasapijob/%d/' % (settings.BASE50URL, job.id),
      ])
    )
    send_mail(
      'WASAPI job %d completed' % (job.id),
      message,
      'donotreply@archive-it.org',
      settings.AITRESEARCHSERVICES_ADDRESS,
      fail_silently=False)
