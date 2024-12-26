// main.js
import { showTab } from "./tabs.js";
import { VPNDrawer } from "./drawer.js";

// Make showTab available globally
window.showTab = showTab;

// Initialize when ready
document.addEventListener("DOMContentLoaded", () => {
  let authToken = "";

  function initializeGoogleSignIn() {
    if (!window.google || !window.google.accounts) {
      setTimeout(initializeGoogleSignIn, 100);
      return;
    }

    console.log("Debug info:", {
      clientId: window.CLIENT_ID,
      origin: window.location.origin,
      pathname: window.location.pathname,
      href: window.location.href,
    });

    // Initialize Google Sign-In
    google.accounts.id.initialize({
      client_id: window.CLIENT_ID,
      callback: handleCredentialResponse,
      state_cookie_domain: window.location.hostname,
      auto_select: true,
      ux_mode: "redirect", // Change to redirect mode
      login_uri: window.location.origin + "/", // URL to redirect back to
      intermediate_iframe_close_callback: () => {
        checkAuthStatus();
      },
    });

    // Render the button
    google.accounts.id.renderButton(document.getElementById("signInDiv"), {
      type: "standard",
      theme: "outline",
      size: "large",
      text: "signin_with",
      width: 250,
    });

    // Check auth status on load
    checkAuthStatus();
  }

  async function checkAuthStatus() {
    try {
      const response = await fetch("/auth-status", {
        credentials: "same-origin",
      });

      const data = await response.json();

      if (data.authenticated) {
        updateCredentialResponse(data);
        showSignedInState(data.email);
      } else {
        // Try to get a new session
        google.accounts.id.prompt((notification) => {
          console.log("Prompt notification:", notification);
        });
      }
    } catch (error) {
      console.error("Error checking auth status:", error);
    }
  }

  async function handleCredentialResponse(response) {
    console.log("Handling credential response...");
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
      console.log("Server response:", data);

      if (data.success && data.token) {
        authToken = data.token;
        checkAuthStatus();
        return authToken;
      } else {
        throw new Error(data.error || "Authentication failed");
      }
    } catch (error) {
      console.error("Authentication error:", error);
      showMessage("Authentication failed: " + error.message, "error");
    }
  }

  function showSignedInState(email) {
    const downloadBtn = document.getElementById("downloadBtn");
    const signInDiv = document.getElementById("signInDiv");
    const setupInstructions = document.getElementById("setupInstructions");
    const authStatus = document.getElementById("authStatus");

    if (downloadBtn) {
      downloadBtn.classList.remove("hidden");
      downloadBtn.style.display = "block";
    }

    if (signInDiv) {
      signInDiv.style.display = "none";
    }

    if (setupInstructions) {
      setupInstructions.style.display = "block";
    }

    if (authStatus) {
      authStatus.textContent = `Authenticated as ${email}`;
    }
  }

  function showMessage(message, type) {
    console.log(`${type}: ${message}`);
    const container = document.querySelector(".container");
    const existingMessage = container.querySelector(
      ".success-message, .error-message"
    );
    if (existingMessage) {
      existingMessage.remove();
    }

    const messageDiv = document.createElement("div");
    messageDiv.className =
      type === "success" ? "success-message" : "error-message";
    messageDiv.textContent = message;
    container.insertBefore(messageDiv, document.querySelector(".status"));
  }

  async function updateCredentialResponse(data) {
    // Find the React component instance and update its state
    const event = new CustomEvent("authStateChanged", {
      detail: {
        isAuthenticated: true,
        token: data.token,
        email: data.email,
      },
    });
    window.dispatchEvent(event);
  }

  // Initialize when ready
  if (document.readyState === "complete") {
    initializeGoogleSignIn();
  } else {
    window.addEventListener("load", initializeGoogleSignIn);
  }
  // Mount React component
  const root = ReactDOM.createRoot(document.getElementById("drawer-root"));
  root.render(React.createElement(VPNDrawer));
});
