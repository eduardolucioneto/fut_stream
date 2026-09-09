from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from chat.models import Message

User = get_user_model()

class ChatMessageDateTimeTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client.login(username='testuser', password='password123')

    def test_message_list_returns_date_and_time_format(self):
        msg = Message.objects.create(user=self.user, content='Olá mundo!')
        response = self.client.get(reverse('message_list'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data['messages']), 1)
        msg_data = data['messages'][0]
        # Must contain DD/MM/YYYY HH:MM format
        self.assertRegex(msg_data['timestamp'], r'^\d{2}/\d{2}/\d{4} \d{2}:\d{2}$')
        self.assertIn('iso_timestamp', msg_data)

