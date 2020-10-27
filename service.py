def ensure_player(func):
    @wraps(func)
    def _ensure_player(request, *args, **kwargs):
        login_info = kwargs.get('login_info')
        player_uuid = login_info.get('player_uuid')
        zone_id = login_info.get('zone_id')
        oauth_id = login_info.get('oauth_id')

        if not player_uuid or not zone_id:
            raise exceptions.SessionAuthException(messages.ERROR__SESSION_EXPIRE)

        player = player_cache_service.get_player_info(player_uuid, zone_id)

        if not player:
            player_db_manager.create_player(player_uuid, zone_id, data={
                'oauth_id': oauth_id,
                'nickname': login_info.get('nickname', ''),
            },)
            player = player_cache_service.get_player_info.update(player_uuid, zone_id)

        if player['nickname'] != login_info.get('nickname'):
            player_db_manager.update_player_info(player_uuid, zone_id, data={'nickname': login_info.get('nickname')})
            player = player_cache_service.get_player_info.update(player_uuid, zone_id)


        return func(request, player=player, *args, **kwargs)
    return _ensure_player