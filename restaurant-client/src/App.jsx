import { useState } from "react";
import ConnectForm from "./components/ConnectForm";
import { getToken } from "./api/token";
import AgentRoom from "./components/AgentRoom";


function App() {
  const [connectionDetails, setConnectionDetails] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleConnect = async ({ identity, room }) => {
    try {
      setLoading(true);

      const data = await getToken(identity, room);

      console.log(data);

      setConnectionDetails({
        token: data.token,
        serverUrl: import.meta.env.VITE_LIVEKIT_URL,
      });

    } catch (err) {
      console.error(err);
      alert("Unable to connect.");
    } finally {
      setLoading(false);
    }
  };

  if (connectionDetails) {
    return (
      <AgentRoom
        token={connectionDetails.token}
        serverUrl={connectionDetails.serverUrl}
      />
    );
  }

  return (
    <ConnectForm
      onConnect={handleConnect}
      loading={loading}
    />
  );
}

export default App;