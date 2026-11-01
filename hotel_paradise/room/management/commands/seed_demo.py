from django.core.management.base import BaseCommand
from room.models import Room


class Command(BaseCommand):
    help = 'Add demo rooms and fill missing Russian translations for unchanged demo content.'

    def handle(self, *args, **options):
        rooms = [
            ('Standard Room', 1, 1, '85.00', 'A comfortable room for a quiet stay.', 'room-1.jpg'),
            ('Deluxe Room', 2, 1, '140.00', 'A spacious room with a seating area and a beautiful view.', 'room-2.jpg'),
            ('Family Suite', 3, 2, '220.00', 'A large suite for families, with space to relax together.', 'room-3.jpg'),
        ]
        translations = {
            'Standard Room': ('Стандартный номер', 'Уютный номер для спокойного отдыха.'),
            'Deluxe Room': ('Номер Делюкс', 'Просторный номер с зоной отдыха и красивым видом.'),
            'Family Suite': ('Семейный люкс', 'Большой семейный номер, где удобно отдыхать вместе.'),
        }
        added = 0
        for title, bedrooms, bathrooms, price, description, image in rooms:
            room, created = Room.objects.get_or_create(title=title, defaults={
                'bedroom_count': bedrooms, 'bathroom_count': bathrooms,
                'price_per_night': price, 'description': description,
                'image': f'static/img/{image}', 'available': True,
                'title_ru': translations[title][0], 'description_ru': translations[title][1],
            })
            if not created:
                changed = []
                if not room.title_ru:
                    room.title_ru = translations[title][0]
                    changed.append('title_ru')
                if not room.description_ru and room.description == description:
                    room.description_ru = translations[title][1]
                    changed.append('description_ru')
                if changed:
                    room.save(update_fields=changed)
            added += created
        self.stdout.write(self.style.SUCCESS(f'Added {added} demo rooms.'))
