const DEFAULT_BACKEND_BASE_URL = "http://127.0.0.1:8000";

export function getBackendBaseUrl() {
  return (process.env.NEXT_PUBLIC_BACKEND_URL ?? DEFAULT_BACKEND_BASE_URL).replace(
    /\/$/,
    "",
  );
}

export function getAvatarUrl(username: string) {
  return `${getBackendBaseUrl()}/avatar/${encodeURIComponent(username)}`;
}
