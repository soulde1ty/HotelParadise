from django.db import models
from django.core.validators import MinValueValidator
from django.templatetags.static import static
from django.utils.translation import get_language, gettext_lazy as _


class Room(models.Model):
    title = models.CharField(max_length=40, default="", verbose_name=_('Title (English)'))
    title_ru = models.CharField(_('Title (Russian)'), max_length=40, blank=True)
    bedroom_count = models.PositiveIntegerField(validators=[MinValueValidator(1)], verbose_name=_('Bedrooms'))
    bathroom_count = models.PositiveIntegerField(validators=[MinValueValidator(1)], verbose_name=_('Bathrooms'))
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], verbose_name=_('Price per night'))
    description = models.TextField(verbose_name=_('Description (English)'))
    description_ru = models.TextField(_('Description (Russian)'), blank=True)
    image = models.ImageField(upload_to="rooms/", blank=True, verbose_name=_('Image'))
    available = models.BooleanField(default=True, verbose_name=_('Open for bookings'))

    class Meta:
        verbose_name = _('Room')
        verbose_name_plural = _('Rooms')

    @property
    def display_title(self):
        if (get_language() or '').startswith('ru') and self.title_ru:
            return self.title_ru
        return self.title

    @property
    def display_description(self):
        if (get_language() or '').startswith('ru') and self.description_ru:
            return self.description_ru
        return self.description

    @property
    def image_url(self):
        if not self.image:
            return static('img/room-1.jpg')
        if self.image.name.startswith('static/'):
            return static(self.image.name.removeprefix('static/'))
        return self.image.url

    def __str__(self):
        return _('%(title)s, %(bedrooms)s Bedroom, %(bathrooms)s Bathroom, $%(price)s') % {
            'title': self.display_title, 'bedrooms': self.bedroom_count,
            'bathrooms': self.bathroom_count, 'price': self.price_per_night,
        }

