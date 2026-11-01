from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch
from django.core.exceptions import ValidationError
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from room.models import Room
from .models import Booking


class BookingFlowTests(TestCase):
    def setUp(self):
        self.room = Room.objects.create(title='Suite', bedroom_count=2, bathroom_count=1,
                                       price_per_night=Decimal('125.50'), description='A room.')
        self.start = timezone.localdate() + timedelta(days=10)
        self.end = self.start + timedelta(days=3)
        self.url = reverse('booking', args=[self.room.pk])
        self.data = {
            'guest_name': 'Test Guest', 'guest_email': 'guest@example.com',
            'check_in': self.start.isoformat(), 'check_out': self.end.isoformat(),
            'room': self.room.pk, 'special_request': '',
        }

    def book(self, start=None, end=None, **extra):
        return Booking.objects.create(
            room=self.room, guest_name='Existing Guest', guest_email='existing@example.com',
            check_in=start or self.start, check_out=end or self.end, **extra)

    def test_booking_calculates_price_and_redirects_without_hiding_room(self):
        response = self.client.post(self.url, {**self.data, 'total_price': '1'}, follow=True)
        self.assertRedirects(response, reverse('room'))
        self.assertContains(response, 'Booking #')
        self.assertContains(response, 'Suite')
        self.assertEqual(Booking.objects.get().total_price, Decimal('376.50'))
        self.room.refresh_from_db()
        self.assertTrue(self.room.available)
        self.client.get(reverse('room'))
        self.assertEqual(Booking.objects.count(), 1)

    def test_invalid_dates_and_email_are_shown_without_saving(self):
        cases = [
            {'check_out': self.start.isoformat()},
            {'check_out': (self.start - timedelta(days=1)).isoformat()},
            {'check_in': (timezone.localdate() - timedelta(days=1)).isoformat()},
            {'check_in': 'not-a-date'},
            {'guest_email': 'not-an-email'},
        ]
        for changes in cases:
            with self.subTest(changes=changes):
                response = self.client.post(self.url, {**self.data, **changes})
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.context['form'].errors)
        self.assertEqual(Booking.objects.count(), 0)

    def test_overlap_boundaries_and_cancelled_bookings(self):
        existing = self.book()
        for start, end in [
            (self.start, self.end),
            (self.start - timedelta(days=1), self.end + timedelta(days=1)),
            (self.start + timedelta(days=1), self.end - timedelta(days=1)),
            (self.start - timedelta(days=1), self.start + timedelta(days=1)),
            (self.end - timedelta(days=1), self.end + timedelta(days=1)),
        ]:
            with self.subTest(start=start, end=end):
                response = self.client.post(self.url, {
                    **self.data, 'check_in': start.isoformat(), 'check_out': end.isoformat()})
                self.assertContains(response, 'already booked')
        self.book(self.start - timedelta(days=2), self.start)
        self.book(self.end, self.end + timedelta(days=2))
        existing.status = Booking.Status.CANCELLED
        existing.save()
        self.assertEqual(self.client.post(self.url, self.data).status_code, 302)

    def test_closed_room_is_rejected_and_get_never_reopens_it(self):
        self.book(timezone.localdate() - timedelta(days=3), timezone.localdate() - timedelta(days=1))
        self.room.available = False
        self.room.save()
        self.client.get(self.url)
        response = self.client.post(self.url, self.data)
        self.assertContains(response, 'closed for bookings')
        self.room.refresh_from_db()
        self.assertFalse(self.room.available)

    def test_selected_room_cannot_be_replaced_by_post_data(self):
        other = Room.objects.create(title='Other', bedroom_count=1, bathroom_count=1, price_per_night=50)
        self.client.post(self.url, {**self.data, 'room': other.pk})
        self.assertEqual(Booking.objects.get().room_id, self.room.pk)

    def test_recheck_at_save_rejects_conflict_after_form_validation(self):
        from .forms import BookingForm
        form = BookingForm(self.data)
        self.assertTrue(form.is_valid())
        self.book()
        with self.assertRaises(ValidationError):
            form.save()
        self.assertEqual(Booking.objects.count(), 1)

    def test_save_conflict_returns_readable_error(self):
        with patch('booking.forms.BookingForm.save', side_effect=ValidationError('Dates just became unavailable.')):
            response = self.client.post(self.url, self.data)
        self.assertContains(response, 'Dates just became unavailable.')

    def test_csrf_and_missing_room(self):
        client = Client(enforce_csrf_checks=True)
        self.assertEqual(client.post(self.url, self.data).status_code, 403)
        self.assertEqual(self.client.get(reverse('booking', args=[99999])).status_code, 404)

    def test_cancellation_keeps_the_original_price(self):
        reservation = self.book()
        Room.objects.filter(pk=self.room.pk).update(price_per_night=999)
        reservation.status = Booking.Status.CANCELLED
        reservation.save()
        reservation.refresh_from_db()
        self.assertEqual(reservation.total_price, Decimal('376.50'))
