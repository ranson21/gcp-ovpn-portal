// src/ovpn_portal/static/src/hooks/useGoogleAuth.js
import { useEffect } from "react";
import { useAuth } from "../context/AuthContext";

export const useGoogleAuth = () => {
  const { updateAuth } = useAuth();

  const handleCredentialResponse = async (response) => {
    try {
      const verifyResponse = await fetch("/", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
          Accept: "application/json",
        },
        body: "credential=" + response.credential,
        credentials: "same-origin",
      });

      const data = await verifyResponse.json();

      if (data.success && data.token) {
        updateAuth({
          email: data.email,
          token: data.token,
        });
        return data.token;
      } else {
        throw new Error(data.error || "Authentication failed");
      }
    } catch (error) {
      console.error("Authentication error:", error);
      // You might want to handle this error in the UI
    }
  };

  const initializeGoogleSignIn = () => {
    // Initialize Google Sign-In
    window.google.accounts.id.initialize({
      client_id: window.CLIENT_ID,
      callback: handleCredentialResponse,
      state_cookie_domain: window.location.hostname,
      auto_select: true,
      ux_mode: "redirect",
      login_uri: window.location.origin + "/",
    });
  };

  useEffect(() => {
    const checkAuthStatus = async () => {
      try {
        const response = await fetch("/auth/status", {
          credentials: "same-origin",
        });

        const data = await response.json();

        if (data.authenticated) {
          updateAuth(data);
        } else {
          // Try to get a new session
          window.google.accounts.id.prompt((notification) => {
            console.log("Prompt notification:", notification);
          });
        }
      } catch (error) {
        console.error("Error checking auth status:", error);
      }
    };

    // Then check at specified interval
    const interval = setInterval(checkAuthStatus, 10000);

    // Cleanup
    return () => {
      clearInterval(interval);
    };
  }, [updateAuth]);

  const renderGoogleButton = (containerId) => {
    if (window.google?.accounts?.id) {
      initializeGoogleSignIn();

      window.google.accounts.id.renderButton(
        document.getElementById(containerId),
        {
          type: "standard",
          theme: "outline",
          size: "large",
          shape: "pill",
          text: "signin_with",
          width: 250,
        }
      );
    }
  };

  return { renderGoogleButton };
};
