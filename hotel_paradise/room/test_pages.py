from datetime import timedelta
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from booking.models import Booking
from .models import Room


class RoomPagesTests(TestCase):
    def setUp(self):
        self.room = Room.objects.create(title='Suite', bedroom_count=2, bathroom_count=1,
                                       price_per_night=100, description='Room without an uploaded image')

    def test_public_pages_work_with_empty_and_populated_catalog(self):
        urls = ['home', 'about', 'service', 'room', 'team', 'testimonial', 'contact', 'booking_general']
        for name in urls:
            with self.subTest(page=name):
                self.assertEqual(self.client.get(reverse(name)).status_code, 200)
        response = self.client.get(reverse('room_detail', args=[self.room.pk]))
        self.assertContains(response, '/static/img/room-1.jpg')
        self.room.delete()
        self.assertContains(self.client.get(reverse('room')), 'No rooms match')

    def test_search_excludes_only_overlapping_confirmed_bookings(self):
        start = timezone.localdate() + timedelta(days=10)
        end = start + timedelta(days=2)
        booking = Booking.objects.create(room=self.room, guest_name='Guest', guest_email='guest@example.com',
                                         check_in=start, check_out=end)
        query = {'check_in': start.isoformat(), 'check_out': end.isoformat()}
        response = self.client.get(reverse('room'), query)
        self.assertNotIn(self.room, response.context['rooms'])
        query = {'check_in': end.isoformat(), 'check_out': (end + timedelta(days=1)).isoformat()}
        response = self.client.get(reverse('room'), query)
        self.assertIn(self.room, response.context['rooms'])
        self.assertContains(response, 'check_in=')
        booking.status = Booking.Status.CANCELLED
        booking.save()
        self.assertIn(self.room, self.client.get(reverse('room'), {
            'check_in': start.isoformat(), 'check_out': end.isoformat()}).context['rooms'])

    def test_filters_and_invalid_input(self):
        self.assertEqual(self.client.get(reverse('room'), {'bedroom_count': 1}).context['rooms'].count(), 0)
        self.assertEqual(self.client.get(reverse('room'), {'bedroom_count': 2, 'bathrooms': 1}).context['rooms'].count(), 1)
        for params in [{'bedroom_count': 'abc'}, {'bathrooms': '-1'}, {'check_in': '2030-01-01'}]:
            response = self.client.get(reverse('room'), params)
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.context['search_form'].errors)

    def test_legacy_and_uploaded_image_paths(self):
        self.room.image = 'static/img/room-2.jpg'
        self.assertEqual(self.room.image_url, '/static/img/room-2.jpg')
        self.room.image = 'rooms/photo.jpg'
        self.assertEqual(self.room.image_url, '/media/rooms/photo.jpg')

    def test_seed_is_repeatable(self):
        call_command('seed_demo', verbosity=0)
        count = Room.objects.count()
        call_command('seed_demo', verbosity=0)
        self.assertEqual(Room.objects.count(), count)
