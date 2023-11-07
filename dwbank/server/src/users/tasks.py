import os
from celery import shared_task
from celery.utils.log import get_task_logger
from users.utils import TemplateEmail
from django.utils.timezone import now
# # from reusable.utils import PersianCalender
from django.conf import settings
from email.mime.image import MIMEImage

# logger = get_task_logger(__name__)


@shared_task(name='send_email')
def send_email(title, receivers, template="base", context=None):
#     # if context:
#     #     context['time']= PersianCalender(now()).to_datetime()
    email_object = TemplateEmail(
        to=receivers,
        subject=title,
        template=template,
        context=context
    )
    image = "logo.png"
    file_path = os.path.join(settings.BASE_DIR, 'templates/emails/logo.png')
    with open(file_path, 'rb') as f:
        img = MIMEImage(f.read())
        img.add_header('Content-ID', '<{name}>'.format(name=image))
        img.add_header('Content-Disposition', 'inline', filename=image)
    email_object.attach_logo(img)
    email_object.send()

