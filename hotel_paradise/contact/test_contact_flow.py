from django.test import TestCase, Client
from django.urls import reverse
from .models import Contact


class ContactFlowTests(TestCase):
    def test_message_is_saved_and_refresh_does_not_duplicate_it(self):
        response = self.client.post(reverse('contact'), {
            'name': 'Guest', 'email': 'guest@example.com', 'subject': 'Arrival',
            'message': 'Can I arrive late?',
        }, follow=True)
        self.assertRedirects(response, reverse('contact'))
        self.assertContains(response, 'Your message has been received')
        self.assertEqual(Contact.objects.count(), 1)
        self.client.get(reverse('contact'))
        self.assertEqual(Contact.objects.count(), 1)

    def test_invalid_message_and_csrf(self):
        response = self.client.post(reverse('contact'), {'email': 'wrong'})
        self.assertTrue(response.context['form'].errors)
        self.assertEqual(Contact.objects.count(), 0)
        self.assertEqual(Client(enforce_csrf_checks=True).post(reverse('contact'), {}).status_code, 403)
