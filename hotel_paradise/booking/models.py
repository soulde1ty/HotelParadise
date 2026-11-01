from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.db import models, transaction
from room.models import Room


class Booking(models.Model):
    class Status(models.TextChoices):
        CONFIRMED = 'confirmed', _('Confirmed')
        CANCELLED = 'cancelled', _('Cancelled')

    guest_name = models.CharField(max_length=100, verbose_name=_('Guest name'))
    guest_email = models.EmailField(verbose_name=_('Guest email'))
    check_in = models.DateField(verbose_name=_('Check-in'))
    check_out = models.DateField(verbose_name=_('Check-out'))
    room = models.ForeignKey(Room, on_delete=models.PROTECT, verbose_name=_('Room'))
    special_request = models.CharField(max_length=300, blank=True, verbose_name=_('Special request'))
    total_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False, verbose_name=_('Total price'))
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.CONFIRMED, verbose_name=_('Status'))

    class Meta:
        verbose_name = _('Booking')
        verbose_name_plural = _('Bookings')
        constraints = [
            models.CheckConstraint(condition=models.Q(check_out__gt=models.F('check_in')), name='booking_positive_stay'),
            models.CheckConstraint(condition=models.Q(total_price__gte=0), name='booking_nonnegative_price'),
        ]
        indexes = [models.Index(fields=['room', 'status', 'check_in', 'check_out'])]

    def clean(self):
        super().clean()
        if not self.check_in or not self.check_out or not self.room_id:
            return
        if self.check_out <= self.check_in:
            raise ValidationError({'check_out': _('Check-out must be after check-in.')})
        if self.status == self.Status.CANCELLED:
            return
        if not self.room.available:
            raise ValidationError({'room': _('This room is currently closed for bookings.')})
        conflicts = Booking.objects.filter(
            room_id=self.room_id, status=self.Status.CONFIRMED,
            check_in__lt=self.check_out, check_out__gt=self.check_in,
        ).exclude(pk=self.pk)
        if conflicts.exists():
            raise ValidationError(_('This room is already booked for the selected dates.'))

    def save(self, *args, **kwargs):
        # A write lock serializes the availability check on SQLite as well as
        # databases with row locks. The availability flag itself is unchanged.
        with transaction.atomic():
            Room.objects.filter(pk=self.room_id).update(available=models.F('available'))
            self.room = Room.objects.get(pk=self.room_id)
            self.full_clean(exclude=['total_price'])
            previous = Booking.objects.filter(pk=self.pk).first() if self.pk else None
            if previous and (previous.room_id, previous.check_in, previous.check_out) == (self.room_id, self.check_in, self.check_out):
                self.total_price = previous.total_price
            else:
                self.total_price = self.room.price_per_night * (self.check_out - self.check_in).days
            self._meta.get_field('total_price').clean(self.total_price, self)
            if kwargs.get('update_fields') is not None:
                kwargs['update_fields'] = set(kwargs['update_fields']) | {'total_price'}
            super().save(*args, **kwargs)

    def __str__(self):
        return _('%(guest)s, %(room)s, %(check_in)s to %(check_out)s, $%(price)s') % {
            'guest': self.guest_name, 'room': self.room.display_title,
            'check_in': self.check_in, 'check_out': self.check_out, 'price': self.total_price,
        }
