from livekit.api import (
    AccessToken,
    VideoGrants
)


class TokenService:


    def __init__(self):

        self.api_key="devkey"
        self.api_secret="secret"



    def create_token(
        self,
        identity,
        room
    ):

        return (
            AccessToken(
                self.api_key,
                self.api_secret
            )
            .with_identity(identity)
            .with_grants(
                VideoGrants(
                    room_join=True,
                    room=room,
                    can_publish=True,
                    can_subscribe=True,
                )
            )
            .to_jwt()
        )