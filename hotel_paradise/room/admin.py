from django.contrib import admin
from .models import Room

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'bedroom_count', 'bathroom_count', 'price_per_night', 'description', 'image', 'available')
    list_editable = ('title', 'bedroom_count', 'bathroom_count', 'price_per_night', 'description', 'image', 'available')
    list_filter = ('price_per_night', 'bedroom_count', 'available')
    search_fields = ('title', 'title_ru', 'description', 'description_ru')



