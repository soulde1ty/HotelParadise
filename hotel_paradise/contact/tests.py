from django.test import TestCase
from .models import Contact

class ContactModelTestCase(TestCase):

    def setUp(self):
        self.contact = Contact.objects.create(
            name="John Doe",
            email="john.doe@example.com",
            subject="Test Subject",
            message="This is a test message."
        )

    def test_contact_creation(self):
        self.assertEqual(self.contact.name, "John Doe")
        self.assertEqual(self.contact.email, "john.doe@example.com")
        self.assertEqual(self.contact.subject, "Test Subject")
        self.assertEqual(self.contact.message, "This is a test message.")

    def test_contact_str_method(self):
        expected_str = "John Doe - john.doe@example.com - Test Subject"
        self.assertEqual(str(self.contact), expected_str)
