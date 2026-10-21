from api.rest_client import RestClient

from api.services.user_service import UserService
from api.services.channel_service import ChannelService
from api.services.chat_service import ChatService
from api.services.activity_service import ActivityService
from api.services.pixels_service import PixelsService
from api.services.subscription_service import SubscriptionService


class VPZoneClient:

    def __init__(self, base_url, api_key=None):

        self.rest = RestClient(
            base_url=base_url,
            api_key=api_key
        )

        # Servicios
        self.users = UserService(self.rest)
        self.channels = ChannelService(self.rest)
        self.chat = ChatService(self.rest)
        self.activity = ActivityService(self.rest)
        self.pixels = PixelsService(self.rest)
        self.subscriptions = SubscriptionService(self.rest)
