from os import path
from random import sample
from django.utils import timezone
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import TemplateDoesNotExist, render_to_string
from django.utils.html import strip_tags
from users.messages import Messages 
from rest_framework.exceptions import ValidationError


def otp_generate():
    chars = "0123456789"
    return "".join(sample(chars, 6))
    

def refrence_id_generate():
    chars = "0123456789"
    return "".join(sample(chars, 9))

class TemplateEmail:
    def __init__(
        self,
        to,
        subject,
        template,
        context={},
        from_email=None,
        reply_to=None,
        **email_kwargs,
    ):
        self.to = to
        self.subject = subject
        self.template = template
        self.context = context
        self.from_email = from_email or settings.EMAIL_HOST_USER
        self.reply_to = reply_to

        self.context["template"] = template

        self.html_content, self.plain_content = self.render_content()

        self.to = self.to if isinstance(self.to, list) else [self.to]

        if self.reply_to:
            self.reply_to = (
                self.reply_to if isinstance(self.reply_to, list) else [self.reply_to]
            )

        self.django_email = EmailMultiAlternatives(
            subject=self.subject,
            body=self.plain_content,
            from_email=self.from_email,
            to=self.to,
            reply_to=self.reply_to,
            **email_kwargs,
        )
        self.django_email.attach_alternative(self.html_content, "text/html")

    def render_content(self):
        html_content = self.render_html()

        try:
            plain_content = self.render_plain()
        except TemplateDoesNotExist:
            plain_content = strip_tags(html_content)

        return html_content, plain_content

    def render_plain(self):
        return render_to_string(self.get_plain_template_name(), self.context)

    def render_html(self):
        return render_to_string(self.get_html_template_name(), self.context)

    def get_plain_template_name(self):
        return f"emails/{self.template}.txt"

    def get_html_template_name(self):
        return f"emails/{self.template}.html"
    
    def attach_logo(self, img):
        return self.django_email.attach(img)

    def send(self, **send_kwargs):
        return self.django_email.send(**send_kwargs)
    

def is_image(ext):
    support_ext = settings.SUPPORTED_IMAGE_FORMATS
    if ext.lower() not in support_ext:
        raise ValidationError(Messages.INVALID_FORMAT.value)
    return True

def id_card_image_path(instance, filename):
    ext = filename.split('.')[-1].lower()
    if is_image(ext):
        return path.join('.','images', 'id_cards', '{}.{}'.format(int(timezone.now().timestamp()), ext))

def passport_image_path(instance, filename):
    ext = filename.split('.')[-1].lower()
    if is_image(ext):
        return path.join('.','images', 'passport', '{}.{}'.format(int(timezone.now().timestamp()), ext))


