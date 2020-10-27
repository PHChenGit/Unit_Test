from datetime import datetime
from unittest.mock import patch, Mock

from django.conf import settings
from django.test import SimpleTestCase
from django.test.client import RequestFactory

class TestEnsurePlayer(SimpleTestCase):
    mock_get_player_info_from_cache = None
    mock_create_player = None

    def setUp(self) -> None:
        get_player_info_from_cache = patch('event.cache_services.player_cache_service.get_player_info')
        self.mock_get_player_info_from_cache = get_player_info_from_cache.start()

        create_player = patch('event.db_managers.player_db_manager.create_player')
        self.mock_create_player = create_player.start()

        self.factory = RequestFactory()
        self.mock_request = self.factory.get('api/info/')

    def tearDown(self) -> None:
        patch.stopall()


    def test_when_player_info_exists_in_cache(self):
        stub_login_info = self.given_stub_player_info({
            'player_uuid': 1000000016,
            'zone_id': 101,
            'oauth_id': '7a302dd49d0aa5c66e034dcc3013b6ea',
            'nickname': 'CK小草莓',
            'group': 'A',
            'first_draw': False,
            'first_draw_at': '',
        }, {
            'player_uuid': 1000000016,
            'zone_id': 101,
            'oauth_id': '7a302dd49d0aa5c66e034dcc3013b6ea',
        })

        self.should_pass(stub_login_info)
        assert self.mock_get_player_info_from_cache.called


    def test_when_player_info_not_exists_in_cache(self):
        stub_login_info = self.given_stub_player_info(None, {
            'player_uuid': 1000000016,
            'zone_id': 101,
            'oauth_id': '7a302dd49d0aa5c66e034dcc3013b6ea',
        })
        self.mock_create_player.return_value = 'player'

        self.should_pass(stub_login_info)
        self.assertEqual(self.mock_get_player_info_from_cache.call_count, 2)
        self.assertEqual(self.mock_create_player.call_count, 0)


    def should_pass(self, stub_login_info):
        excepted = 'success'
        mock_func = Mock(return_value=excepted)
        decorated_func = ensure_player(mock_func)
        act = decorated_func(self.mock_request, login_info=stub_login_info)
        assert act == excepted


    def given_stub_player_info(self, player_info_cache: dict, login_info: dict):
        self.mock_get_player_info_from_cache.return_value = player_info_cache
        stub_login_info = login_info
        return stub_login_info