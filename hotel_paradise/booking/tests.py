from datetime import date
from django.test import TestCase
from room.models import Room
from booking.models import Booking

class BookingModelTestCase(TestCase):
    def setUp(self):
        self.room = Room.objects.create(
            title="Standard Room",
            bedroom_count=2,
            bathroom_count=1,
            price_per_night=100,
            description="A cozy room with a view",
            available=True
        )
        self.booking = Booking.objects.create(
            guest_name="John Doe",
            guest_email="aboba@gmail.com",
            check_in="2021-10-01",
            check_out="2021-10-05",
            room=self.room,
            special_request="No special request",
            total_price=400
        )

    def test_booking_creation(self):
        self.assertEqual(self.booking.guest_name, "John Doe")
        self.assertEqual(self.booking.guest_email, "aboba@gmail.com")
        self.assertEqual(self.booking.check_in, date(2021, 10, 1))
        self.assertEqual(self.booking.check_out, date(2021, 10, 5))
        self.assertEqual(self.booking.room, self.room)
        self.assertEqual(self.booking.special_request, "No special request")
        self.assertEqual(self.booking.total_price, 400)

    def test_booking_str_method(self):
        expected_str = "John Doe, Standard Room, 2021-10-01 to 2021-10-05, $400.00"
        self.assertEqual(str(self.booking), expected_str)
