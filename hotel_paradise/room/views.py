from urllib.parse import urlencode
from django.shortcuts import get_object_or_404, render
from booking.models import Booking
from .forms import RoomSearchForm
from .models import Room


def room(request):
    form = RoomSearchForm(request.GET or None)
    rooms = Room.objects.filter(available=True).order_by('price_per_night', 'pk')
    dates_query = ''
    if form.is_bound:
        if form.is_valid():
            data = form.cleaned_data
            if data['bedroom_count']:
                rooms = rooms.filter(bedroom_count=data['bedroom_count'])
            if data['bathrooms']:
                rooms = rooms.filter(bathroom_count=data['bathrooms'])
            if data['check_in'] and data['check_out']:
                conflicts = Booking.objects.filter(
                    status=Booking.Status.CONFIRMED,
                    check_in__lt=data['check_out'], check_out__gt=data['check_in'],
                ).values('room_id')
                rooms = rooms.exclude(pk__in=conflicts)
                dates_query = urlencode({key: data[key].isoformat() for key in ('check_in', 'check_out')})
        else:
            rooms = rooms.none()
    return render(request, 'room_main.html', {'rooms': rooms, 'search_form': form, 'dates_query': dates_query})


def room_detail(request, room_id):
    selected_room = get_object_or_404(Room, pk=room_id)
    return render(request, 'room_detail.html', {'room': selected_room})
