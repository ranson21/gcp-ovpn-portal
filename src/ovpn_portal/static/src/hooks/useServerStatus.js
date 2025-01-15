import { useState, useEffect } from "react";

export const useServerStatus = (pollingInterval = 10000) => {
  const [serverStatus, setServerStatus] = useState({
    isActive: false,
    isOperational: false,
    loading: true,
  });

  useEffect(() => {
    const checkServerStatus = async () => {
      try {
        const response = await fetch("/health");
        const data = await response.json();

        setServerStatus({
          isActive: true,
          isOperational: data.status === "healthy",
          loading: false,
        });
      } catch (error) {
        console.error("Error checking server status:", error);
        setServerStatus({
          isActive: false,
          isOperational: false,
          loading: false,
        });
      }
    };

    // Check immediately
    checkServerStatus();

    // Then check at specified interval
    const interval = setInterval(checkServerStatus, pollingInterval);

    // Cleanup on unmount
    return () => clearInterval(interval);
  }, [pollingInterval]);

  return serverStatus;
};
