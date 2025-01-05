import React, { useState } from "react";

import { DownloadLink } from "../DownloadLink";
import { InstructionCard } from "../InstructionCard";
import { CommandBlock } from "../CommandBlock";
import { useAuth } from "../../context/AuthContext";

export const VPNSetupInstructions = () => {
  const { isAuthenticated } = useAuth();
  const [activeTab, setActiveTab] = useState("windows");

  const tabs = {
    windows: {
      label: "Windows",
      content: (
        <div className="space-y-6">
          <InstructionCard title="Step 1: Download OpenVPN Client">
            <DownloadLink href="https://openvpn.net/downloads/openvpn-connect-v3-windows.msi">
              Download OpenVPN Connect for Windows
            </DownloadLink>
          </InstructionCard>

          <InstructionCard title="Step 2: Install OpenVPN Connect">
            <ol className="list-decimal pl-6 space-y-2">
              <li>Double-click the downloaded MSI file</li>
              <li>Follow the installation wizard</li>
              <li>Accept the default settings when prompted</li>
            </ol>
          </InstructionCard>

          <InstructionCard title="Step 3: Import Configuration">
            <ol className="list-decimal pl-6 space-y-2">
              <li>
                Download your personal client.ovpn file using the button in the
                left panel
              </li>
              <li>Double-click the downloaded .ovpn file</li>
              <li>
                OpenVPN Connect will automatically import the configuration
              </li>
              <li>Click "Connect" to establish the VPN connection</li>
            </ol>
          </InstructionCard>
        </div>
      ),
    },
    mac: {
      label: "macOS",
      content: (
        <div className="space-y-6">
          <InstructionCard title="Step 1: Download OpenVPN Client">
            <DownloadLink href="https://openvpn.net/downloads/openvpn-connect-v3-macos.dmg">
              Download OpenVPN Connect for macOS
            </DownloadLink>
          </InstructionCard>

          <InstructionCard title="Step 2: Install OpenVPN Connect">
            <ol className="list-decimal pl-6 space-y-2">
              <li>Open the downloaded .dmg file</li>
              <li>Drag OpenVPN Connect to the Applications folder</li>
              <li>Launch OpenVPN Connect from Applications</li>
              <li>Allow system extensions if prompted</li>
            </ol>
          </InstructionCard>

          <InstructionCard title="Step 3: Import Configuration">
            <ol className="list-decimal pl-6 space-y-2">
              <li>
                Download your personal client.ovpn file using the button in the
                left panel
              </li>
              <li>Open OpenVPN Connect</li>
              <li>
                Drag and drop the .ovpn file into the OpenVPN Connect window
              </li>
              <li>Click "Add" to import the profile</li>
              <li>Click "Connect" to establish the VPN connection</li>
            </ol>
          </InstructionCard>
        </div>
      ),
    },
    linux: {
      label: "Linux",
      content: (
        <div className="space-y-6">
          <InstructionCard title="Debian/Ubuntu Installation">
            <p className="mb-4">
              Open terminal and run the following commands:
            </p>
            <CommandBlock>{`sudo apt update
sudo apt install openvpn`}</CommandBlock>
          </InstructionCard>

          <InstructionCard title="Fedora/RHEL Installation">
            <p className="mb-4">
              Open terminal and run the following commands:
            </p>
            <CommandBlock>sudo dnf install openvpn</CommandBlock>
          </InstructionCard>

          <InstructionCard title="Import Configuration">
            <ol className="list-decimal pl-6 space-y-2">
              <li>
                Download your personal client.ovpn file using the button in the
                left panel
              </li>
              <li>Move the configuration file to the OpenVPN directory:</li>
              <CommandBlock>
                sudo mv ~/Downloads/client.ovpn /etc/openvpn/client/
              </CommandBlock>
              <li>Start the VPN connection:</li>
              <CommandBlock>
                sudo openvpn --config /etc/openvpn/client/client.ovpn
              </CommandBlock>
              <li>Or enable it as a system service:</li>
              <CommandBlock>
                sudo systemctl enable --now openvpn-client@client
              </CommandBlock>
            </ol>
          </InstructionCard>
        </div>
      ),
    },
  };

  return (
    <div className="main-content">
      <img
        src="dist/images/openvpn_logo.png"
        alt="OpenVPN Logo"
        className="h-16 w-auto"
      />

      <h1 className="text-2xl font-bold mb-4">OpenVPN Client Portal</h1>
      <p className="mb-4">To download your VPN configuration:</p>
      <ol className="list-decimal pl-6 mb-8 space-y-2">
        <li>Sign in with your organization account</li>
        <li>Download your personalized OpenVPN configuration file</li>
        <li>Import the configuration into your OpenVPN client</li>
      </ol>

      {isAuthenticated && (
        <div className="mt-8">
          <h2 className="text-xl font-semibold mb-6">VPN Setup Instructions</h2>

          <div className="mb-6">
            <nav className="flex space-x-4" aria-label="Tabs">
              {Object.entries(tabs).map(([key, { label }]) => (
                <button
                  key={key}
                  onClick={() => setActiveTab(key)}
                  className={`
                  tab-button 
                  ${activeTab === key ? "active" : ""}
                `}
                >
                  {label}
                </button>
              ))}
            </nav>
          </div>

          <div className="mt-6">{tabs[activeTab].content}</div>
        </div>
      )}
    </div>
  );
};
