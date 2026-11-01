from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'guest_name', 'guest_email', 'room', 'check_in', 'check_out', 'status', 'total_price')
    list_filter = ('status', 'check_in', 'check_out', 'room')
    search_fields = ('guest_name', 'guest_email', 'room__title')
    readonly_fields = ('total_price',)
    actions = ['cancel_bookings']

    @admin.action(description=_('Cancel selected bookings'))
    def cancel_bookings(self, request, queryset):
        count = queryset.update(status=Booking.Status.CANCELLED)
        self.message_user(request, _('Cancelled bookings: %(count)s.') % {'count': count})
