from django.utils.translation import gettext_lazy as _
from django.db import models


class Contact(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    email = models.EmailField(verbose_name=_('Email'))
    subject = models.CharField(max_length=50, verbose_name=_('Subject'))
    message = models.TextField(verbose_name=_('Message'))

    class Meta:
        verbose_name = _('Guest message')
        verbose_name_plural = _('Guest messages')

    def __str__(self):
        return f"{self.name} - {self.email} - {self.subject}"
