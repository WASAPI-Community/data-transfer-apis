from django.conf import settings
from django.core.mail import send_mail


class Mailer(object):
    """Send an email for various events"""

    def new_wasapijob(sender, instance, **kwargs):
        # would prefer to call the parameter "job", but "send" passes it by name
        job = instance
        message_template = """
Dear Web Archivists,

The account "{account_name:s}" ({account_id:d}) has submitted a new job ({job_id:d}):
{function:s}
{query:s}

{wasapi_url:s}
{admin_url:s}

Love,
WASAPI within AIT5
"""
        message = message_template.format(
          account_name = job.account.organization_name,
          account_id = job.account.id,
          job_id = job.id,
          function = job.function,
          query = job.query,
          wasapi_url = settings.BASE50URL + job.get_absolute_url(),
          admin_url = '%s/admin/wasapi/wasapijob/%d/' % (
            settings.BASE50URL, job.id))
        send_mail(
          'Research Services Dataset Request via WASAPI',
          message,
          'donotreply@archive-it.org',
          settings.AITRESEARCHSERVICES_ADDRESS,
          fail_silently=False)
