// src/ovpn_portal/static/src/components/Drawer/index.jsx
import React, { useEffect, useRef } from "react";

import { useVpnStatus } from "../../hooks/useVpnStatus";
import { NetworkMetrics } from "./NetworkMetrics";
import { ConnectionDiagnostics } from "./ConnectionDiagnostics";
import { useAuth } from "../../context/AuthContext";
import { useGoogleAuth } from "../../hooks/useGoogleAuth";

export const VPNDrawer = () => {
  const { isAuthenticated, email, token } = useAuth();
  const vpnStatus = useVpnStatus();
  const { renderGoogleButton } = useGoogleAuth();
  const signInDivRef = useRef(null);

  // Initialize Google Sign-in button
  useEffect(() => {
    if (!isAuthenticated && signInDivRef.current) {
      renderGoogleButton("signInDiv");
    }
  }, [isAuthenticated, renderGoogleButton]);

  const handleDownload = async () => {
    if (!token) return;

    try {
      const response = await fetch("/vpn/download-config", {
        headers: {
          Authorization: `Bearer ${token}`,
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
      console.error("Download error:", error);
      alert("Error downloading configuration: " + error.message);
    }
  };

  return (
    <div className="w-128 h-screen bg-gray-50 border-r border-gray-200 p-6 fixed left-0 top-0">
      <div className="flex flex-col h-full">
        {/* Logo Section */}
        <div className="flex items-center space-x-2 mb-8">
          <div className="h-8">
            <img
              src="/static/images/openvpn_logo.png"
              alt="OpenVPN Logo"
              className="h-full"
            />
          </div>
        </div>

        {/* Auth Status */}
        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200 mb-6">
          <div className="text-sm font-medium text-gray-800 mb-2">
            Authentication
          </div>
          <div className="text-xs text-gray-600">
            {isAuthenticated ? `Signed in: ${email}` : "Not authenticated"}
          </div>
        </div>

        {/* Network Status */}
        <NetworkMetrics
          isConnected={vpnStatus.connected}
          clientIp={vpnStatus.clientIp}
        />

        {/* Connection Diagnostics */}
        {vpnStatus.connected && (
          <ConnectionDiagnostics isConnected={vpnStatus.connected} />
        )}

        {/* Download Button */}
        {isAuthenticated ? (
          <button
            onClick={handleDownload}
            className="mt-auto w-full bg-orange-700 text-white px-4 py-2 rounded-lg hover:bg-orange-800 flex items-center justify-center space-x-2"
          >
            <svg
              className="w-4 h-4"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
            >
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3" />
            </svg>
            <span>Download Config</span>
          </button>
        ) : (
          <div
            id="signInDiv"
            ref={signInDivRef}
            className="mt-4 flex justify-center"
          />
        )}
      </div>
    </div>
  );
};
