import { useState } from "react";

export default function ConnectForm({ onConnect, loading }) {
  const [identity, setIdentity] = useState("Fatima");
  const [room, setRoom] = useState("restaurant");

  const handleSubmit = (e) => {
    e.preventDefault();

    onConnect({
      identity,
      room,
    });
  };

  return (
    <form onSubmit={handleSubmit}>
      <h2>Restaurant Voice Assistant</h2>

      <div>
        <label>Name</label>

        <input
          value={identity}
          onChange={(e) => setIdentity(e.target.value)}
        />
      </div>

      <br />

      <div>
        <label>Room</label>

        <input
          value={room}
          onChange={(e) => setRoom(e.target.value)}
        />
      </div>

      <br />
    <button
        type="submit"
        disabled={loading}
    >
        {loading ? "Connecting..." : "Connect"}
    </button>
    </form>
  );
}