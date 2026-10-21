from api.models.channel import Channel


class ChannelService:

    def __init__(self, rest):

        self.rest = rest

    def get(self, slug):

        data = self.rest.get(
            f"/channels/{slug}"
        )

        return Channel.from_json(data)
