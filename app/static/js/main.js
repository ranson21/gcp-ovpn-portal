let authToken = "";

function initializeGoogleSignIn() {
  if (!window.google || !window.google.accounts) {
    setTimeout(initializeGoogleSignIn, 100);
    return;
  }

  console.log("Debug info:", {
    clientId: CLIENT_ID,
    origin: window.location.origin,
    pathname: window.location.pathname,
    href: window.location.href,
  });

  // Initialize Google Sign-In
  google.accounts.id.initialize({
    client_id: CLIENT_ID,
    callback: handleCredentialResponse,
    state_cookie_domain: window.location.hostname,
    auto_select: true,
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
      showSignedInState(data.email);
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
  if (downloadBtn) {
    downloadBtn.classList.remove("hidden");
    downloadBtn.style.display = "block";
  }
  showMessage(`Authenticated as ${email}`, "success");
}

// Initialize when ready
if (document.readyState === "complete") {
  initializeGoogleSignIn();
} else {
  window.addEventListener("load", initializeGoogleSignIn);
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
