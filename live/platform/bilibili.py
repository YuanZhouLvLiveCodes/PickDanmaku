from live.platform.base_platform import BasePlatform


class BiliApi(BasePlatform):
    def __init__(self, room_id, **kwargs):
        super().__init__(room_id, **kwargs)

    def _get_user_info(self, user_id):
        pass
