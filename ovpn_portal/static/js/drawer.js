// drawer.js
export const VPNDrawer = () => {
  const [isAuthenticated, setIsAuthenticated] = React.useState(false);
  const [authToken, setAuthToken] = React.useState(null);
  const [authEmail, setAuthEmail] = React.useState(null);
  const [vpnStatus, setVpnStatus] = React.useState({
    connected: false,
    clientIp: null,
    loading: true,
  });
  const [serverStatus, setServerStatus] = React.useState({
    isActive: false,
    isOperational: false,
    loading: true,
  });

  // Listen for authentication state changes
  React.useEffect(() => {
    const handleAuthState = (event) => {
      setIsAuthenticated(event.detail.isAuthenticated);
      setAuthToken(event.detail.token);
      setAuthEmail(event.detail.email);
    };

    window.addEventListener("authStateChanged", handleAuthState);
    return () =>
      window.removeEventListener("authStateChanged", handleAuthState);
  }, []);

  // Poll server status
  React.useEffect(() => {
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

    // Then check every 30 seconds
    const interval = setInterval(checkServerStatus, 10000);

    return () => clearInterval(interval);
  }, []);

  // Poll VPN connection status
  React.useEffect(() => {
    const getNetworkIPs = () => {
      return new Promise((resolve, reject) => {
        const ips = new Set();
        const RTCPeerConnection =
          window.RTCPeerConnection ||
          window.webkitRTCPeerConnection ||
          window.mozRTCPeerConnection;

        if (!RTCPeerConnection) {
          reject(new Error("WebRTC not supported"));
          return;
        }

        // Set a timeout to force completion
        const timeout = setTimeout(() => {
          if (pc) pc.close();
          resolve(Array.from(ips));
        }, 1000); // Shorter timeout

        const pc = new RTCPeerConnection({
          iceServers: [{ urls: "stun:stun.l.google.com:19302" }],
          iceCandidatePoolSize: 1, // Minimize candidates
        });

        pc.createDataChannel("");

        pc.onicecandidate = (e) => {
          if (!e.candidate) {
            clearTimeout(timeout);
            pc.close();
            resolve(Array.from(ips));
            return;
          }

          const ipMatch =
            /([0-9]{1,3}(\.[0-9]{1,3}){3}|[a-f0-9]{1,4}(:[a-f0-9]{1,4}){7})/i.exec(
              e.candidate.candidate
            );
          if (ipMatch && ipMatch[1]) {
            ips.add(ipMatch[1]);
          }
        };

        pc.createOffer()
          .then((offer) => pc.setLocalDescription(offer))
          .catch((err) => {
            clearTimeout(timeout);
            pc.close();
            reject(err);
          });
      });
    };

    const checkVpnStatus = async () => {
      setVpnStatus((prev) => ({ ...prev, loading: true }));

      try {
        const ips = await getNetworkIPs();

        // Get the VPN network from window globals
        const vpnNetworkPrefix =
          window.VPN_NETWORK?.split(".").slice(0, 2).join(".") || "10.8";

        // Check if any of our IPs are in the VPN range
        const isVpnConnected = ips.some((ip) => {
          try {
            return ip.startsWith(vpnNetworkPrefix);
          } catch (err) {
            console.error("Error checking IP:", err);
            return false;
          }
        });

        setVpnStatus({
          connected: isVpnConnected,
          clientIp: ips.find((ip) => ip.startsWith("10.8.")) || ips[0],
          allIps: ips,
          loading: false,
        });
      } catch (error) {
        console.error("Error checking VPN status:", error);
        setVpnStatus({
          connected: false,
          clientIp: "Unknown",
          loading: false,
        });
      }
    };

    // Check immediately
    checkVpnStatus();

    // Then check every 30 seconds instead of 10
    const interval = setInterval(checkVpnStatus, 10000);

    return () => clearInterval(interval);
  }, []);

  // Download handler
  const handleDownload = async () => {
    if (!authToken) {
      alert("Please authenticate first");
      return;
    }

    try {
      const response = await fetch("/download-config", {
        headers: {
          Authorization: "Bearer " + authToken,
        },
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "client.ovpn";
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } else {
        const error = await response.json();
        throw new Error(error.error || "Download failed");
      }
    } catch (error) {
      console.error("Error:", error);
      alert("Error downloading configuration: " + error.message);
    }
  };

  return React.createElement(
    "div",
    {
      className:
        "w-64 h-screen bg-gray-50 border-r border-gray-200 p-6 fixed left-0 top-0",
    },
    React.createElement(
      "div",
      {
        className: "flex flex-col h-full",
      },
      [
        // Logo Section
        React.createElement(
          "div",
          {
            className: "flex items-center space-x-2 mb-8",
            key: "logo",
          },
          [
            // OpenVPN Logo
            React.createElement(
              "div",
              {
                className: "h-8 flex items-center",
                key: "openvpn-logo",
              },
              React.createElement(
                "svg",
                {
                  height: "32",
                  viewBox: "0 0 240 80",
                  className: "h-full w-auto",
                  fill: "none",
                  xmlns: "http://www.w3.org/2000/svg",
                },
                [
                  // Shield background
                  React.createElement("path", {
                    d: "M28 72s32-16 32-40V12L28 0 0 12v20c0 24 28 40 28 40z",
                    fill: "#F78B1F", // OpenVPN orange
                    key: "shield",
                  }),
                  // Lock symbol
                  React.createElement("path", {
                    d: "M28 16c-4.4 0-8 3.6-8 8v4h-4v16h24V28h-4v-4c0-4.4-3.6-8-8-8zm0 4c2.2 0 4 1.8 4 4v4H24v-4c0-2.2 1.8-4 4-4z",
                    fill: "white",
                    key: "lock",
                  }),
                  // Text
                  React.createElement(
                    "text",
                    {
                      x: "70",
                      y: "45",
                      style: {
                        fontFamily: "Arial, sans-serif",
                        fontSize: "32px",
                        fontWeight: "bold",
                        fill: "#333333",
                      },
                      key: "text",
                    },
                    "OpenVPN"
                  ),
                ]
              )
            ),
          ]
        ),

        // Status Card
        React.createElement(
          "div",
          {
            className: "bg-white rounded-lg shadow-sm p-6 mb-6",
            key: "status",
          },
          [
            // Server Status
            React.createElement(
              "div",
              {
                className: "flex items-center space-x-2 mb-4",
                key: "status-indicator",
              },
              [
                React.createElement("div", {
                  className: `h-2 w-2 rounded-full ${
                    serverStatus.loading
                      ? "bg-gray-300"
                      : serverStatus.isActive && serverStatus.isOperational
                      ? "bg-green-500"
                      : "bg-red-500"
                  }`,
                }),
                React.createElement(
                  "span",
                  {
                    className: `text-sm font-medium ${
                      serverStatus.loading
                        ? "text-gray-500"
                        : serverStatus.isActive && serverStatus.isOperational
                        ? "text-green-700"
                        : "text-red-700"
                    }`,
                  },
                  serverStatus.loading
                    ? "Checking Status..."
                    : serverStatus.isActive && serverStatus.isOperational
                    ? "Server Active"
                    : "Server Offline"
                ),
              ]
            ),
            React.createElement(
              "div",
              {
                className:
                  "flex items-center justify-between text-sm text-gray-600 border-t border-gray-100 pt-4",
                key: "status-details",
              },
              [
                React.createElement("span", null, "Server Status"),
                React.createElement(
                  "div",
                  {
                    className: "flex items-center space-x-1",
                  },
                  serverStatus.loading
                    ? [
                        React.createElement("div", {
                          className:
                            "animate-spin rounded-full h-4 w-4 border-2 border-gray-300 border-t-gray-600",
                        }),
                        React.createElement(
                          "span",
                          {
                            className: "text-gray-600",
                          },
                          "Checking..."
                        ),
                      ]
                    : [
                        React.createElement(
                          "svg",
                          {
                            className: `h-4 w-4 ${
                              serverStatus.isOperational
                                ? "text-green-500"
                                : "text-red-500"
                            }`,
                            viewBox: "0 0 24 24",
                            fill: "none",
                            stroke: "currentColor",
                            strokeWidth: "2",
                          },
                          serverStatus.isOperational
                            ? React.createElement("polyline", {
                                points: "20 6 9 17 4 12",
                              })
                            : React.createElement("line", {
                                x1: "18",
                                y1: "6",
                                x2: "6",
                                y2: "18",
                              })
                        ),
                        React.createElement(
                          "span",
                          {
                            className: serverStatus.isOperational
                              ? "text-green-600"
                              : "text-red-600",
                          },
                          serverStatus.isOperational ? "Operational" : "Offline"
                        ),
                      ]
                ),
              ]
            ),
            // VPN Connection Status
            React.createElement(
              "div",
              {
                className:
                  "flex items-center justify-between text-sm text-gray-600 border-t border-gray-100 pt-4 mt-4",
                key: "vpn-status",
              },
              [
                React.createElement("span", null, "VPN Connection"),
                React.createElement(
                  "div",
                  {
                    className: "flex items-center space-x-1",
                  },
                  vpnStatus.loading
                    ? [
                        React.createElement("div", {
                          className:
                            "animate-spin rounded-full h-4 w-4 border-2 border-gray-300 border-t-gray-600",
                        }),
                        React.createElement(
                          "span",
                          {
                            className: "text-gray-600",
                          },
                          "Checking..."
                        ),
                      ]
                    : [
                        React.createElement(
                          "svg",
                          {
                            className: `h-4 w-4 ${
                              vpnStatus.connected
                                ? "text-green-500"
                                : "text-red-500"
                            }`,
                            viewBox: "0 0 24 24",
                            fill: "none",
                            stroke: "currentColor",
                            strokeWidth: "2",
                          },
                          vpnStatus.connected
                            ? React.createElement("polyline", {
                                points: "20 6 9 17 4 12",
                              })
                            : React.createElement("line", {
                                x1: "18",
                                y1: "6",
                                x2: "6",
                                y2: "18",
                              })
                        ),
                        React.createElement(
                          "span",
                          {
                            className: vpnStatus.connected
                              ? "text-green-600"
                              : "text-red-600",
                          },
                          vpnStatus.connected ? "Connected" : "Disconnected"
                        ),
                      ]
                ),
              ]
            ),
            vpnStatus.clientIp &&
              React.createElement(
                "div",
                {
                  className: "text-xs text-gray-500 mt-2",
                  key: "client-ip",
                },
                [
                  React.createElement(
                    "div",
                    { key: "current-ip" },
                    `Current IP: ${vpnStatus.clientIp}`
                  ),
                  window.location.hostname === "localhost" &&
                    vpnStatus.allIps &&
                    React.createElement(
                      "div",
                      {
                        className: "text-xs mt-1 text-gray-400",
                        key: "all-ips",
                      },
                      `All IPs: ${vpnStatus.allIps.join(", ")}`
                    ),
                ]
              ),
          ]
        ),

        // Auth Section
        React.createElement(
          "div",
          {
            className: "space-y-4",
            key: "auth",
          },
          React.createElement(
            "div",
            {
              className:
                "bg-white p-4 rounded-lg shadow-sm border border-gray-200",
            },
            [
              React.createElement(
                "div",
                {
                  className: "text-sm font-medium text-gray-800 mb-2",
                  key: "auth-title",
                },
                "Authentication"
              ),
              React.createElement(
                "div",
                {
                  className: "text-xs text-gray-600 mb-4",
                  key: "auth-status",
                },
                isAuthenticated
                  ? `Signed in: ${authEmail}`
                  : "Not authenticated"
              ),
              React.createElement("div", {
                id: "signInDiv",
                className: "w-full scale-90 origin-left",
                key: "sign-in",
              }),
            ]
          )
        ),

        // Download Button
        React.createElement(
          "div",
          {
            className: "mt-auto",
            key: "download",
          },
          React.createElement(
            "button",
            {
              className: `w-full flex items-center justify-center space-x-2 px-4 py-2 bg-orange-700 text-white rounded-lg hover:bg-orange-800 ${
                !isAuthenticated ? "opacity-50 cursor-not-allowed" : ""
              }`,
              disabled: !isAuthenticated,
              onClick: handleDownload,
            },
            [
              React.createElement(
                "svg",
                {
                  className: "h-4 w-4",
                  viewBox: "0 0 24 24",
                  fill: "none",
                  stroke: "currentColor",
                  strokeWidth: "2",
                  key: "download-icon",
                },
                React.createElement("path", {
                  d: "M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3",
                })
              ),
              React.createElement(
                "span",
                {
                  key: "download-text",
                },
                "Download Config"
              ),
            ]
          )
        ),

        // Footer
        React.createElement(
          "div",
          {
            className: "mt-6 text-center",
            key: "footer",
          },
          React.createElement(
            "p",
            {
              className: "text-xs text-gray-500",
            },
            "OpenVPN • v2.5.1"
          )
        ),
      ]
    )
  );
};
