import logging
import os

from dotenv import load_dotenv

from .system_prompt import Assistant

from livekit.agents import (
    AgentServer,
    AgentSession,
    JobContext,
    TurnHandlingOptions,
    cli,
    room_io,
)

from livekit.plugins import (
    deepgram,
    cartesia,
    groq,
    ai_coustics,
    silero,
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)


logger = logging.getLogger("restaurant-agent")


load_dotenv()


logger.info("Environment loaded")

logger.info(
    "LIVEKIT_URL: %s",
    os.getenv("LIVEKIT_URL")
)


server = AgentServer()



@server.rtc_session(agent_name="restaurant-agent")
async def restaurant_agent(ctx: JobContext):

    logger.info(
        "Agent joining room: %s",
        ctx.room.name
    )


    await ctx.connect()


    logger.info(
        "Connected to LiveKit room"
    )


    session = AgentSession(

        # Speech to Text
        stt=deepgram.STT(
            model="nova-3",
            language="multi",
        ),


        # Text to Speech
        tts=cartesia.TTS(
            model="sonic-3",
            voice="9626c31c-bec5-4cca-baa8-f8ba9e84c8bc",
        ),


        # LLM
        llm=groq.LLM(
            model="qwen/qwen3.6-27b"
        ),


        # Voice Activity Detection (VAD)
        vad=silero.VAD.load(),


        turn_handling=TurnHandlingOptions(
            turn_detection="vad"
        ),


        preemptive_generation=True,
    )


    assistant = Assistant()


    await session.start(
        agent=assistant,
        room=ctx.room,
    )


    logger.info(
        "Restaurant agent started successfully"
    )



if __name__ == "__main__":

    cli.run_app(server)