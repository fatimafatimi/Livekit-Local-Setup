export async function getToken(identity, room) {
  const response = await fetch(
    `${import.meta.env.VITE_API_URL}/api/token?identity=${identity}&room=${room}`
  );

  if (!response.ok) {
    throw new Error("Failed to fetch token");
  }

  return response.json();
}