from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class TestimonialConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'testimonial'
    verbose_name = _('Reviews')
