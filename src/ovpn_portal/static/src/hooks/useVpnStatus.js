import { useState, useEffect } from "react";

export const useVpnStatus = () => {
  const [status, setVpnStatus] = useState({
    connected: false,
    clientIp: null,
    loading: true,
  });

  useEffect(() => {
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

    checkVpnStatus();
    const interval = setInterval(checkVpnStatus, 10000);
    return () => clearInterval(interval);
  }, []);

  return status;
};
