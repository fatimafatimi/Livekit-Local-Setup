import os

from livekit import api


class LiveKitService:

    def __init__(self):
        self.client = api.LiveKitAPI(
            url=os.getenv("LIVEKIT_URL"),
            api_key=os.getenv("LIVEKIT_API_KEY"),
            api_secret=os.getenv("LIVEKIT_API_SECRET"),
        )

    async def dispatch_agent(self, room_name):
        await self.client.agent_dispatch.create_dispatch(
            api.CreateAgentDispatchRequest(
                room=room_name,
                agent_name="restaurant-agent",
            )
        )