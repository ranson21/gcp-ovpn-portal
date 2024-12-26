const ConnectionDiagnostics = ({ isConnected }) => {
  const [diagnostics, setDiagnostics] = React.useState({
    dns: { status: "pending", latency: null },
    connectivity: { status: "pending", details: [] },
    stability: {
      status: "pending",
      samples: [],
      drops: 0,
      averageLatency: null,
    },
  });

  // Test DNS resolution
  const checkDNS = async () => {
    const domains = ["google.com", "amazon.com", "microsoft.com"];
    const results = [];

    for (const domain of domains) {
      const start = performance.now();
      try {
        await fetch(`https://${domain}/favicon.ico`, { mode: "no-cors" });
        const latency = performance.now() - start;
        results.push({ success: true, latency });
      } catch (error) {
        results.push({ success: false, latency: null });
      }
    }

    const successCount = results.filter((r) => r.success).length;
    const avgLatency =
      results
        .filter((r) => r.success)
        .reduce((acc, curr) => acc + curr.latency, 0) / successCount || 0;

    return {
      status: successCount >= 2 ? "healthy" : "issue",
      latency: Math.round(avgLatency),
    };
  };

  // Basic connectivity check
  const checkConnectivity = async () => {
    const checks = [
      { name: "VPN Endpoint", url: "/health" },
      {
        name: "DNS Resolution",
        url: "https://1.1.1.1/favicon.ico",
        mode: "no-cors",
      },
      {
        name: "External Access",
        url: "https://www.google.com/favicon.ico",
        mode: "no-cors",
      },
    ];

    const results = [];
    for (const check of checks) {
      try {
        const start = performance.now();
        await fetch(check.url, check.mode ? { mode: check.mode } : {});
        results.push({
          name: check.name,
          status: "success",
          latency: Math.round(performance.now() - start),
        });
      } catch (error) {
        results.push({
          name: check.name,
          status: "failed",
          error: error.message,
        });
      }
    }

    return {
      status: results.every((r) => r.status === "success")
        ? "healthy"
        : "issue",
      details: results,
    };
  };

  // Monitor connection stability
  const monitorStability = async () => {
    const sampleSize = 5;
    const samples = [];
    let drops = 0;

    for (let i = 0; i < sampleSize; i++) {
      try {
        const start = performance.now();
        await fetch("/health");
        samples.push(performance.now() - start);
      } catch (error) {
        drops++;
        samples.push(null);
      }
      // Small delay between samples
      await new Promise((resolve) => setTimeout(resolve, 200));
    }

    const validSamples = samples.filter((s) => s !== null);
    const averageLatency = validSamples.length
      ? Math.round(
          validSamples.reduce((a, b) => a + b, 0) / validSamples.length
        )
      : null;

    return {
      status: drops <= 1 ? "stable" : drops <= 2 ? "unstable" : "poor",
      samples: samples,
      drops: drops,
      averageLatency,
    };
  };

  // Run all diagnostics
  const runDiagnostics = async () => {
    setDiagnostics((prev) => ({
      ...prev,
      dns: { ...prev.dns, status: "checking" },
      connectivity: { ...prev.connectivity, status: "checking" },
      stability: { ...prev.stability, status: "checking" },
    }));

    const [dnsResults, connectivityResults, stabilityResults] =
      await Promise.all([checkDNS(), checkConnectivity(), monitorStability()]);

    setDiagnostics({
      dns: dnsResults,
      connectivity: connectivityResults,
      stability: stabilityResults,
    });
  };

  // Run diagnostics on mount and when connection status changes
  React.useEffect(() => {
    runDiagnostics();
    const interval = setInterval(runDiagnostics, 60000); // Run every minute
    return () => clearInterval(interval);
  }, [isConnected]);

  // Helper for status indicators
  const StatusIndicator = ({ status, text }) => {
    const getStatusColor = (status) => {
      switch (status) {
        case "healthy":
        case "stable":
          return "bg-green-500";
        case "unstable":
        case "issue":
          return "bg-yellow-500";
        case "poor":
          return "bg-red-500";
        case "checking":
          return "bg-blue-500 animate-pulse";
        default:
          return "bg-gray-500";
      }
    };

    return React.createElement(
      "div",
      {
        className: "flex items-center space-x-2",
      },
      [
        React.createElement("div", {
          className: `h-2 w-2 rounded-full ${getStatusColor(status)}`,
        }),
        React.createElement(
          "span",
          {
            className: "text-sm",
          },
          text
        ),
      ]
    );
  };

  return React.createElement(
    "div",
    {
      className: "bg-white rounded-lg shadow-sm p-4 mb-4",
    },
    [
      // Header
      React.createElement(
        "div",
        {
          className: "flex items-center justify-between mb-4",
          key: "header",
        },
        [
          React.createElement(
            "h3",
            {
              className: "text-sm font-medium text-gray-800 max-w-24",
            },
            "Connection Diagnostics"
          ),
          diagnostics.dns.status === "checking"
            ? React.createElement("div", { className: "flex" }, [
                React.createElement(
                  "span",
                  { className: "text-xs text-blue-600 mr-2" },
                  "Running Tests..."
                ),

                React.createElement("div", {
                  className:
                    "animate-spin rounded-full h-4 w-4 border-2 border-gray-300 border-t-gray-600",
                }),
              ])
            : React.createElement(
                "button",
                {
                  className:
                    "text-xs text-blue-600 hover:text-blue-800 text-right",
                  onClick: runDiagnostics,
                },
                "Run Tests"
              ),
        ]
      ),

      // DNS Status
      React.createElement(
        "div",
        {
          className: "mb-3",
          key: "dns",
        },
        [
          React.createElement(StatusIndicator, {
            status: diagnostics.dns.status,
            text: `DNS Resolution: ${
              diagnostics.dns.status === "checking"
                ? "Checking..."
                : diagnostics.dns.status === "healthy"
                ? `Healthy (${diagnostics.dns.latency}ms)`
                : "Issues Detected"
            }`,
          }),
        ]
      ),

      // Connectivity Status
      React.createElement(
        "div",
        {
          className: "mb-3",
          key: "connectivity",
        },
        [
          React.createElement(StatusIndicator, {
            status: diagnostics.connectivity.status,
            text: `Connectivity: ${
              diagnostics.connectivity.status === "checking"
                ? "Checking..."
                : diagnostics.connectivity.status === "healthy"
                ? "All Services Reachable"
                : "Some Services Unreachable"
            }`,
          }),
          diagnostics.connectivity.details.map((detail, index) =>
            React.createElement(
              "div",
              {
                className: "ml-4 text-xs text-gray-500 mt-1",
                key: `detail-${index}`,
              },
              `${detail.name}: ${
                detail.status === "success" ? `${detail.latency}ms` : "Failed"
              }`
            )
          ),
        ]
      ),

      // Stability Status
      React.createElement(
        "div",
        {
          className: "mb-3",
          key: "stability",
        },
        [
          React.createElement(StatusIndicator, {
            status: diagnostics.stability.status,
            text: `Connection Stability: ${
              diagnostics.stability.status === "checking"
                ? "Checking..."
                : diagnostics.stability.status === "stable"
                ? `Stable (avg ${diagnostics.stability.averageLatency}ms)`
                : diagnostics.stability.status === "unstable"
                ? "Minor Issues Detected"
                : "Unstable Connection"
            }`,
          }),
          diagnostics.stability.drops > 0 &&
            React.createElement(
              "div",
              {
                className: "ml-4 text-xs text-gray-500 mt-1",
              },
              `Packet Loss: ${((diagnostics.stability.drops / 5) * 100).toFixed(
                1
              )}%`
            ),
        ]
      ),
    ]
  );
};

// NetworkMetrics component within the same file
const NetworkMetrics = ({ isConnected, clientIp }) => {
  const [metrics, setMetrics] = React.useState({
    location: { city: "Loading...", country: "...", region: "", loading: true },
    latency: { value: null, loading: true },
    connectionQuality: { status: "checking", loading: true },
  });

  // Helper function to determine connection quality based on latency
  const getConnectionQuality = (latency) => {
    if (!latency) return { status: "unknown", color: "gray" };
    if (latency < 50) return { status: "Excellent", color: "green" };
    if (latency < 100) return { status: "Good", color: "green" };
    if (latency < 200) return { status: "Fair", color: "yellow" };
    return { status: "Poor", color: "red" };
  };

  React.useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const start = performance.now();

        // Try ip-api.com instead of ipapi.co (more generous rate limits)
        const locationResponse = await fetch("http://ip-api.com/json/");
        if (!locationResponse.ok) {
          throw new Error("Location API request failed");
        }

        const locationData = await locationResponse.json();
        const latencyValue = Math.round(performance.now() - start);
        const quality = getConnectionQuality(latencyValue);

        // Map ip-api.com response format to our expected format
        setMetrics({
          location: {
            city: locationData.city,
            region: locationData.region,
            country: locationData.country,
            isp: locationData.isp,
            loading: false,
          },
          latency: {
            value: latencyValue,
            loading: false,
          },
          connectionQuality: {
            status: quality.status,
            color: quality.color,
            loading: false,
          },
        });
      } catch (error) {
        console.error("Error fetching metrics:", error);
        // Set error state but keep trying
        setMetrics((prev) => ({
          ...prev,
          location: {
            city: "Error loading",
            region: "Unkown",
            country: "Unknown",
            isp: "Unknown",
            loading: false,
          },
          latency: {
            value: null,
            loading: false,
          },
          connectionQuality: {
            status: "unknown",
            color: "gray",
            loading: false,
          },
        }));
      }
    };

    fetchMetrics();
    const interval = setInterval(fetchMetrics, 10000);
    return () => clearInterval(interval);
  }, [isConnected]);

  return React.createElement(
    "div",
    {
      className: "bg-white rounded-lg shadow-sm p-4 mb-4",
    },
    [
      // Connection Status
      React.createElement(
        "div",
        {
          className: "mb-4 border-b border-gray-100 pb-4",
          key: "connection-status",
        },
        [
          React.createElement(
            "div",
            {
              className: "flex items-center justify-between mb-2",
            },
            [
              React.createElement(
                "h3",
                {
                  className: "text-sm font-medium text-gray-800",
                },
                "Connection Status"
              ),
              React.createElement(
                "span",
                {
                  className: `px-2 py-1 text-xs rounded-full ${
                    isConnected
                      ? "bg-green-100 text-green-800"
                      : "bg-gray-100 text-gray-800"
                  }`,
                },
                isConnected ? "Connected" : "Not Connected"
              ),
            ]
          ),

          // Connection Quality
          !metrics.connectionQuality.loading &&
            React.createElement(
              "div",
              {
                className: "flex items-center mt-2 justify-between",
              },
              [
                React.createElement(
                  "span",
                  {
                    className: "text-sm text-gray-600 mr-2",
                  },
                  "Connection Quality:"
                ),
                React.createElement(
                  "span",
                  {
                    className: `text-sm font-medium text-right ${
                      metrics.connectionQuality.color === "green"
                        ? "text-green-600"
                        : metrics.connectionQuality.color === "yellow"
                        ? "text-yellow-600"
                        : metrics.connectionQuality.color === "red"
                        ? "text-red-600"
                        : "text-gray-600"
                    }`,
                  },
                  metrics.connectionQuality.status
                ),
              ]
            ),
        ]
      ),

      // Connection Details
      React.createElement(
        "div",
        {
          className: "space-y-3",
          key: "connection-details",
        },
        [
          // Current Location
          React.createElement(
            "div",
            {
              className: "flex justify-between items-center text-sm",
            },
            [
              React.createElement(
                "span",
                { className: "text-gray-600" },
                "Location"
              ),
              React.createElement(
                "span",
                { className: "font-medium text-right max-w-28" },
                metrics.location.loading
                  ? "Loading..."
                  : `${metrics.location.city}, ${metrics.location.region} ${metrics.location.country}`
              ),
            ]
          ),

          // ISP Info
          React.createElement(
            "div",
            {
              className: "flex justify-between items-center text-sm",
            },
            [
              React.createElement(
                "span",
                { className: "text-gray-600 max-w-24" },
                "Network Provider"
              ),
              React.createElement(
                "span",
                { className: "font-medium text-right max-w-28" },
                metrics.location.loading
                  ? "Loading..."
                  : metrics.location.isp || "Unknown"
              ),
            ]
          ),

          // IP Address
          React.createElement(
            "div",
            {
              className: "flex justify-between items-center text-sm",
            },
            [
              React.createElement(
                "span",
                { className: "text-gray-600" },
                "IP Address"
              ),
              React.createElement(
                "span",
                { className: "font-medium" },
                clientIp || "Unknown"
              ),
            ]
          ),

          // Response Time
          React.createElement(
            "div",
            {
              className: "flex justify-between items-center text-sm",
            },
            [
              React.createElement(
                "span",
                { className: "text-gray-600" },
                "Response Time"
              ),
              React.createElement(
                "span",
                {
                  className: `font-medium ${
                    metrics.latency.value < 100
                      ? "text-green-600"
                      : metrics.latency.value < 200
                      ? "text-yellow-600"
                      : "text-red-600"
                  }`,
                },
                metrics.latency.loading
                  ? "Loading..."
                  : `${metrics.latency.value}ms`
              ),
            ]
          ),
        ]
      ),
    ]
  );
};

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
        "w-128 h-screen bg-gray-50 border-r border-gray-200 p-6 fixed left-0 top-0",
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

        // Auth Section
        React.createElement(
          "div",
          {
            className: "space-y-4 mb-6",
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
            ]
          ),
          React.createElement("div", {
            id: "signInDiv",
            className: "w-full scale-90",
            key: "sign-in",
          })
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
          ]
        ),

        // Network Metrics
        React.createElement(NetworkMetrics, {
          isConnected: vpnStatus.connected,
          clientIp: vpnStatus.clientIp,
          key: "network-metrics",
        }),

        // Connection Diagnostics (only show when connected)
        vpnStatus.connected &&
          React.createElement(ConnectionDiagnostics, {
            isConnected: vpnStatus.connected,
            key: "connection-diagnostics",
          }),

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
