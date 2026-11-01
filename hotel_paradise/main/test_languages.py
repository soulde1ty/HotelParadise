from datetime import timedelta
from io import StringIO
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone, translation
from room.models import Room
from booking.models import Booking


class LanguageTests(TestCase):
    def setUp(self):
        self.room = Room.objects.create(
            title='Standard Room', title_ru='Стандартный номер',
            description='A comfortable room.', description_ru='Уютный номер.',
            bedroom_count=1, bathroom_count=1, price_per_night='85.00',
        )

    def set_language(self, language, next_page='/'):
        return self.client.post(reverse('set_language'), {'language': language, 'next': next_page})

    def test_switch_remembers_language_and_keeps_search_dates(self):
        next_page = '/room/?check_in=2030-06-10&check_out=2030-06-12'
        response = self.set_language('ru', next_page)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, next_page)
        self.assertEqual(response.cookies[settings.LANGUAGE_COOKIE_NAME].value, 'ru')
        response = self.client.get(next_page)
        self.assertContains(response, '<html lang="ru">')
        self.assertContains(response, 'Найти номера')
        self.assertContains(response, 'value="2030-06-10"')
        self.assertContains(response, 'Стандартный номер')
        self.set_language('en', next_page)
        response = self.client.get(next_page)
        self.assertContains(response, '<html lang="en">')
        self.assertContains(response, 'Search rooms')
        self.assertContains(response, 'Standard Room')
        self.assertNotContains(response, 'Стандартный номер')

    def test_all_public_pages_render_in_both_languages(self):
        paths = [reverse(name) for name in (
            'home', 'about', 'service', 'room', 'booking_general', 'team', 'testimonial', 'contact')]
        paths += [reverse('booking', args=[self.room.pk]), reverse('room_detail', args=[self.room.pk])]
        for language, contact_label in [('en', 'Contact our team'), ('ru', 'Связаться с нами')]:
            self.set_language(language)
            for path in paths:
                with self.subTest(language=language, path=path):
                    response = self.client.get(path)
                    self.assertEqual(response.status_code, 200)
                    self.assertContains(response, f'<html lang="{language}">')
                    self.assertContains(response, contact_label)
                    self.assertNotContains(response, '{% translate')
                    self.assertNotContains(response, 'Tempor erat')

    def test_accept_language_cookie_precedence_and_client_isolation(self):
        response = self.client.get('/', HTTP_ACCEPT_LANGUAGE='ru-RU,ru;q=0.9,en;q=0.8')
        self.assertContains(response, '<html lang="ru">')
        self.set_language('en')
        self.assertContains(self.client.get('/', HTTP_ACCEPT_LANGUAGE='ru'), '<html lang="en">')
        self.assertContains(Client().get('/'), '<html lang="en">')

    def test_booking_success_errors_and_optional_room_selection_are_russian(self):
        self.set_language('ru')
        start = timezone.localdate() + timedelta(days=3)
        data = {'guest_name': 'Гость', 'guest_email': 'guest@example.com',
                'check_in': start.isoformat(), 'check_out': (start + timedelta(days=2)).isoformat(),
                'room': self.room.pk}
        form_page = self.client.get(reverse('booking_general'))
        self.assertContains(form_page, 'Стандартный номер')
        self.assertContains(form_page, 'Дата заезда')
        invalid = self.client.post(reverse('booking_general'), {**data, 'check_out': start.isoformat()})
        self.assertContains(invalid, 'Дата выезда должна быть позже даты заезда.')
        response = self.client.post(reverse('booking_general'), data, follow=True)
        self.assertContains(response, 'подтверждено. Итого: $170,00.')
        self.assertEqual(Booking.objects.count(), 1)
        response = self.client.post(reverse('booking_general'), data)
        self.assertContains(response, 'Этот номер уже забронирован на выбранные даты.')

    def test_contact_errors_and_confirmation_are_russian(self):
        self.set_language('ru')
        response = self.client.post(reverse('contact'), {})
        self.assertContains(response, 'Обязательное поле.')
        self.assertContains(response, 'Электронная почта')
        response = self.client.post(reverse('contact'), {
            'name': 'Гость', 'email': 'guest@example.com', 'subject': 'Заезд', 'message': 'Вопрос о заезде.',
        }, follow=True)
        self.assertContains(response, 'Спасибо! Ваше сообщение получено.')

    def test_admin_model_names_and_translation_fields(self):
        user = get_user_model().objects.create_superuser('admin', 'admin@example.com', 'test-password')
        self.client.force_login(user)
        self.set_language('ru')
        response = self.client.get(reverse('admin:index'))
        self.assertContains(response, 'Бронирования')
        self.assertContains(response, 'Сообщения гостей')
        response = self.client.get(reverse('admin:room_room_change', args=[self.room.pk]))
        self.assertContains(response, 'Название (русский)')
        self.assertContains(response, 'Описание (английский)')

    def test_room_fallback_and_seed_preserve_custom_translations(self):
        with translation.override('ru'):
            self.assertEqual(self.room.display_title, 'Стандартный номер')
            self.room.title_ru = ''
            self.assertEqual(self.room.display_title, 'Standard Room')
        self.room.title_ru = 'Моё название'
        self.room.save()
        call_command('seed_demo', stdout=StringIO())
        self.room.refresh_from_db()
        self.assertEqual(self.room.title_ru, 'Моё название')
        deluxe = Room.objects.get(title='Deluxe Room')
        self.assertEqual(deluxe.title_ru, 'Номер Делюкс')
        self.assertTrue(deluxe.description_ru)

    def test_switch_requires_csrf_and_rejects_external_redirect(self):
        client = Client(enforce_csrf_checks=True)
        self.assertEqual(client.post(reverse('set_language'), {'language': 'ru'}).status_code, 403)
        response = self.set_language('ru', 'https://example.org/unsafe')
        self.assertEqual(response.url, '/')
