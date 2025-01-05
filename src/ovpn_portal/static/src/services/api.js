const API_ENDPOINTS = {
  health: "/health",
  authStatus: "/auth/status",
  downloadConfig: "/download-config",
};

export async function downloadConfig(token) {
  const response = await fetch(API_ENDPOINTS.downloadConfig, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || "Download failed");
  }

  return response.blob();
}
