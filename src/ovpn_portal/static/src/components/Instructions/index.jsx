import React from "react";
import { useAuth } from "../../context/AuthContext";

const PlatformTab = ({ id, title, children, active, onClick }) => (
  <div className={`tab-content ${active ? "active" : ""}`} id={id}>
    <div className="instruction-card">
      <h3>{title}</h3>
      {children}
    </div>
  </div>
);

export const Instructions = () => {
  const { isAuthenticated } = useAuth();
  const [activeTab, setActiveTab] = React.useState("windows");

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="main-content">
      <h2>VPN Setup Instructions</h2>

      <div className="tabs">
        <button
          className={`tab-button ${activeTab === "windows" ? "active" : ""}`}
          onClick={() => setActiveTab("windows")}
        >
          Windows
        </button>
        <button
          className={`tab-button ${activeTab === "mac" ? "active" : ""}`}
          onClick={() => setActiveTab("mac")}
        >
          macOS
        </button>
        <button
          className={`tab-button ${activeTab === "linux" ? "active" : ""}`}
          onClick={() => setActiveTab("linux")}
        >
          Linux
        </button>
      </div>

      <PlatformTab
        id="windows"
        title="Windows Setup"
        active={activeTab === "windows"}
      >
        <ol>
          <li>
            <a
              href="https://openvpn.net/downloads/openvpn-connect-v3-windows.msi"
              className="download-link"
            >
              Download OpenVPN Connect for Windows
            </a>
          </li>
          <li>Double-click the downloaded MSI file</li>
          <li>Follow the installation wizard</li>
          <li>Import your downloaded .ovpn file</li>
          <li>Connect to VPN</li>
        </ol>
      </PlatformTab>

      <PlatformTab id="mac" title="macOS Setup" active={activeTab === "mac"}>
        <ol>
          <li>
            <a
              href="https://openvpn.net/downloads/openvpn-connect-v3-macos.dmg"
              className="download-link"
            >
              Download OpenVPN Connect for macOS
            </a>
          </li>
          <li>Open the downloaded .dmg file</li>
          <li>Drag OpenVPN Connect to Applications</li>
          <li>Launch OpenVPN Connect</li>
          <li>Import your downloaded .ovpn file</li>
        </ol>
      </PlatformTab>

      <PlatformTab
        id="linux"
        title="Linux Setup"
        active={activeTab === "linux"}
      >
        <div className="linux-instructions">
          <h4>Debian/Ubuntu:</h4>
          <pre>sudo apt update && sudo apt install openvpn</pre>

          <h4>Fedora/RHEL:</h4>
          <pre>sudo dnf install openvpn</pre>

          <h4>Import Configuration:</h4>
          <pre>sudo mv ~/Downloads/client.ovpn /etc/openvpn/client/</pre>
          <pre>sudo systemctl enable --now openvpn-client@client</pre>
        </div>
      </PlatformTab>
    </div>
  );
};
