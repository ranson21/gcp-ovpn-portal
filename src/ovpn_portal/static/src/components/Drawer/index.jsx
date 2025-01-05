import React, { Fragment } from "react";

import { useVpnStatus } from "../../hooks/useVpnStatus";
import { NetworkMetrics } from "../NetworkMetrics";
import { ConnectionDiagnostics } from "../ConnectionDiagnostics";
import { useAuth } from "../../context/AuthContext";
import { OpenVPNLogo } from "../Logo";
import { AuthStatus } from "../AuthStatus";
import { DownloadConfig } from "../DownloadConfig";
import { StatusCard } from "../VPNStatus";
import { DrawerFooter } from "../DrawerFooter";

export const VPNDrawer = () => {
  const { isAuthenticated, email, token } = useAuth();
  const vpnStatus = useVpnStatus();

  return (
    <div className="w-128 h-screen bg-gray-50 border-r border-gray-200 p-6 fixed left-0 top-0">
      <div className="flex flex-col h-full">
        {/* Logo Section */}
        <OpenVPNLogo />

        {/* Auth Status */}
        <AuthStatus isAuthenticated={isAuthenticated} email={email} />

        {isAuthenticated && (
          <Fragment>
            {/* Server Status */}
            <StatusCard pollingInterval={10000} />

            {/* Network Status */}
            <NetworkMetrics
              isConnected={vpnStatus.connected}
              clientIp={vpnStatus.clientIp}
            />

            {/* Connection Diagnostics */}
            {vpnStatus.connected && (
              <ConnectionDiagnostics isConnected={vpnStatus.connected} />
            )}
          </Fragment>
        )}

        {/* Download Button */}
        <DownloadConfig isAuthenticated={isAuthenticated} token={token} />

        {/* Footer */}
        <DrawerFooter />
      </div>
    </div>
  );
};
