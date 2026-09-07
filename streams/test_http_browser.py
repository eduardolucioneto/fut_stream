import json
import os
from pathlib import Path
import subprocess
from unittest import skipUnless

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import Client, override_settings
from django.urls import reverse
from django.utils import timezone

from schedule.models import GameEvent
from .models import StreamRoom


@skipUnless(os.environ.get('FUTSTREAM_BROWSER_TEST') == '1', 'Optional Chrome/Playwright test')
@override_settings(DEBUG=True, SECURE_SSL_REDIRECT=False, SESSION_COOKIE_SECURE=False, CSRF_COOKIE_SECURE=False)
class HttpStreamingBrowserTest(StaticLiveServerTestCase):
    def test_video_without_websocket_and_with_http_recovery(self):
        host = get_user_model().objects.create_user('browser_host')
        viewer = get_user_model().objects.create_user('browser_viewer')
        game = GameEvent.objects.create(title='Video Test', date_time=timezone.now(),
            team_a='A', team_b='B', created_by=host)
        room = StreamRoom.objects.create(host=host, game=game, title='Video Test', is_live=True)
        cookies = []
        for user in (host, viewer):
            client = Client()
            client.force_login(user)
            cookies.append({'name': settings.SESSION_COOKIE_NAME,
                            'value': client.cookies[settings.SESSION_COOKIE_NAME].value,
                            'url': self.live_server_url})
        env = {**os.environ, 'FUTSTREAM_BROWSER_FIXTURE': json.dumps({
            'baseURL': self.live_server_url,
            'hostPath': reverse('broadcast_room', args=[room.pk]),
            'watchPath': reverse('watch_stream', args=[game.pk]),
            'cookies': cookies,
        })}
        result = subprocess.run(['node', str(Path(__file__).parent / 'js_tests/http-browser-smoke.cjs')],
                                env=env, capture_output=True, text=True, timeout=180)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        print(result.stdout)
