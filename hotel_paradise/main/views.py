from django.shortcuts import render
from room.forms import RoomSearchForm
from room.models import Room


def home(request):
    return render(request, 'main.html', {
        'rooms': Room.objects.filter(available=True).order_by('price_per_night', 'pk')[:3],
        'search_form': RoomSearchForm(),
    })
