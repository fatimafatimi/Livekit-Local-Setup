from fastapi import APIRouter

from src.services.token_service import TokenService
from src.services.livekit_service import LiveKitService


router = APIRouter(
    prefix="/api",
    tags=["LiveKit"]
)


token_service = TokenService()
livekit_service = LiveKitService()



@router.get("/token")
async def get_token(identity: str, room: str):

    token = token_service.create_token(
        identity,
        room
    )


    await livekit_service.dispatch_agent(
        room
    )


    return {
        "token": token,
        "identity": identity,
        "room": room,
    }