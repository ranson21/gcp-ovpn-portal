// src/ovpn_portal/static/src/hooks/useGoogleAuth.js
import { useEffect } from "react";
import { useAuth } from "../context/AuthContext";

export const useGoogleAuth = () => {
  const { updateAuth } = useAuth();

  useEffect(() => {
    const initializeGoogleSignIn = () => {
      if (!window.google || !window.google.accounts) {
        setTimeout(initializeGoogleSignIn, 100);
        return;
      }

      // Initialize Google Sign-In
      window.google.accounts.id.initialize({
        client_id: window.CLIENT_ID,
        callback: handleCredentialResponse,
        state_cookie_domain: window.location.hostname,
        auto_select: true,
        ux_mode: "redirect",
        login_uri: window.location.origin + "/",
      });

      // Check existing auth status
      checkAuthStatus();
    };

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

    // Initialize when ready
    if (document.readyState === "complete") {
      initializeGoogleSignIn();
    } else {
      window.addEventListener("load", initializeGoogleSignIn);
    }

    // Cleanup
    return () => {
      window.removeEventListener("load", initializeGoogleSignIn);
    };
  }, [updateAuth]);

  const renderGoogleButton = (containerId) => {
    if (window.google?.accounts?.id) {
      window.google.accounts.id.renderButton(
        document.getElementById(containerId),
        {
          type: "standard",
          theme: "outline",
          size: "large",
          text: "signin_with",
          width: 250,
        }
      );
    }
  };

  return { renderGoogleButton };
};
