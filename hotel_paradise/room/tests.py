from django.test import TestCase
from room.models import Room

class RoomModelTestCase(TestCase):

    def setUp(self):
        self.standard_room = Room.objects.create(
            title="Standard Room",
            bedroom_count=2,
            bathroom_count=1,
            price_per_night=100,
            description="A cozy room with a view",
            available=True
        )
        self.deluxe_room = Room.objects.create(
            title="Deluxe Room",
            bedroom_count=3,
            bathroom_count=2,
            price_per_night=200,
            description="A luxurious room with a sea view",
            available=False
        )

    def test_standard_room_creation(self):
        self.assertEqual(self.standard_room.title, "Standard Room")
        self.assertEqual(self.standard_room.bedroom_count, 2)
        self.assertEqual(self.standard_room.bathroom_count, 1)
        self.assertEqual(self.standard_room.price_per_night, 100)
        self.assertEqual(self.standard_room.description, "A cozy room with a view")
        self.assertEqual(self.standard_room.available, True)

    def test_deluxe_room_creation(self):
        self.assertEqual(self.deluxe_room.title, "Deluxe Room")
        self.assertEqual(self.deluxe_room.bedroom_count, 3)
        self.assertEqual(self.deluxe_room.bathroom_count, 2)
        self.assertEqual(self.deluxe_room.price_per_night, 200)
        self.assertEqual(self.deluxe_room.description, "A luxurious room with a sea view")
        self.assertEqual(self.deluxe_room.available, False)

    def test_standard_room_str_method(self):
        expected_str = "Standard Room, 2 Bedroom, 1 Bathroom, $100"
        self.assertEqual(str(self.standard_room), expected_str)

    def test_deluxe_room_str_method(self):
        expected_str = "Deluxe Room, 3 Bedroom, 2 Bathroom, $200"
        self.assertEqual(str(self.deluxe_room), expected_str)
