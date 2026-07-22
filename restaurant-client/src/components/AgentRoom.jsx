import {
  LiveKitRoom,
  RoomAudioRenderer,
  VoiceAssistantControlBar,
} from "@livekit/components-react";

import "@livekit/components-styles";


export default function AgentRoom({
  token,
  serverUrl,
}) {

  return (
    <LiveKitRoom
    token={token}
    serverUrl={serverUrl}
    connect={true}
    audio={true}
    video={false}
>
    <RoomAudioRenderer />

    <h2>
       Restaurant Assistant Connected 🎤
    </h2>

    <VoiceAssistantControlBar />

</LiveKitRoom>
  );
}