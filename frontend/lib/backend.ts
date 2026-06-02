const LOCAL_BACKEND_BASE_URL = "http://127.0.0.1:8000";
const PRODUCTION_BACKEND_BASE_URL =
  "https://donut-trades-backend-bjgnb8ajfsa0hhev.westus3-01.azurewebsites.net";

function getDefaultBackendBaseUrl() {
  return process.env.NODE_ENV === "production"
    ? PRODUCTION_BACKEND_BASE_URL
    : LOCAL_BACKEND_BASE_URL;
}

export function getBackendBaseUrl() {
  return (
    process.env.NEXT_PUBLIC_BACKEND_URL ?? getDefaultBackendBaseUrl()
  ).replace(/\/$/, "");
}

export function getAvatarUrl(username: string) {
  return `${getBackendBaseUrl()}/avatar/${encodeURIComponent(username)}`;
}
