from django.contrib import messages
from django.utils.translation import gettext as _
from django.utils.formats import number_format
from django.core.exceptions import ValidationError
from django.db import OperationalError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods
from room.models import Room
from .forms import BookingForm


@require_http_methods(['GET', 'POST'])
def booking(request, room_id=None):
    selected_room = get_object_or_404(Room, pk=room_id) if room_id else None
    form = BookingForm(
        request.POST if request.method == 'POST' else None,
        selected_room=selected_room,
        initial={key: request.GET.get(key, '') for key in ('check_in', 'check_out')},
    )
    if request.method == 'POST' and form.is_valid():
        try:
            reservation = form.save()
        except ValidationError as error:
            form.add_error(None, ' '.join(error.messages))
        except OperationalError as error:
            if 'locked' not in str(error).lower():
                raise
            form.add_error(None, _('Another booking is being processed. Please try again.'))
        else:
            messages.success(request, _('Booking #%(number)s confirmed. Total: $%(total)s.') % {
                'number': reservation.pk, 'total': number_format(reservation.total_price, decimal_pos=2),
            })
            return redirect('room')
    return render(request, 'booking_main.html', {'form': form, 'selected_room': selected_room})
