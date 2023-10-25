import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _


class BaseManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

class BaseModel(models.Model):
    """
    Base model for inheritence for another models.
    """
    id = models.UUIDField(_("ID"), primary_key=True, default=uuid.uuid4, editable=False)
    updated_at = models.DateTimeField(_("Updated_At"), auto_now=True)
    created_at = models.DateTimeField(_("Created_At"), auto_now_add=True)
    is_deleted = models.BooleanField(_("Is_Deleted"), default=False)
    objects = BaseManager()

    class Meta:
        abstract = True

