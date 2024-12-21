// drawer.js
export const VPNDrawer = () => {
  const [isAuthenticated, setIsAuthenticated] = React.useState(false);
  const [authToken, setAuthToken] = React.useState(null);
  const [authEmail, setAuthEmail] = React.useState(null);

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
            React.createElement(
              "svg",
              {
                className: "h-6 w-6 text-blue-600",
                viewBox: "0 0 24 24",
                fill: "none",
                stroke: "currentColor",
                strokeWidth: "2",
                key: "shield-icon",
              },
              React.createElement("path", {
                d: "M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z",
              })
            ),
            React.createElement(
              "h2",
              {
                className: "text-lg font-semibold text-gray-900",
              },
              "VPN Portal"
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
            React.createElement(
              "div",
              {
                className: "flex items-center space-x-2 mb-4",
                key: "status-indicator",
              },
              [
                React.createElement("div", {
                  className: "h-2 w-2 rounded-full bg-green-500",
                }),
                React.createElement(
                  "span",
                  {
                    className: "text-sm font-medium text-green-700",
                  },
                  "Server Active"
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
                React.createElement("span", null, "Status"),
                React.createElement(
                  "div",
                  {
                    className: "flex items-center space-x-1",
                  },
                  [
                    React.createElement(
                      "svg",
                      {
                        className: "h-4 w-4 text-green-500",
                        viewBox: "0 0 24 24",
                        fill: "none",
                        stroke: "currentColor",
                        strokeWidth: "2",
                      },
                      React.createElement("polyline", {
                        points: "20 6 9 17 4 12",
                      })
                    ),
                    React.createElement(
                      "span",
                      {
                        className: "text-green-600",
                      },
                      "Operational"
                    ),
                  ]
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
                "bg-white p-4 rounded-lg shadow-sm border border-gray-200 overflow-hidden",
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
                  className: "text-xs text-gray-600 mb-4 truncate",
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
            className: "w-full scale-90 origin-left",
            key: "sign-in",
          })
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
              className: `w-full flex items-center justify-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 ${
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
