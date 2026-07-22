import '@livekit/components-styles';
console.log("VoiceRoom rendered");

import {
  LiveKitRoom,
  RoomAudioRenderer,
} from '@livekit/components-react';

export default function VoiceRoom({
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

      <div style={{ padding: 20 }}>
        <h2>Connected to LiveKit 🎉</h2>

        <p>You are now inside the room.</p>
      </div>
    </LiveKitRoom>
  );
}