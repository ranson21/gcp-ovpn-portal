import React, { useEffect, useRef } from "react";
import { useGoogleAuth } from "../../hooks/useGoogleAuth";

export const DownloadConfig = ({ isAuthenticated, token }) => {
  const { renderGoogleButton } = useGoogleAuth();
  const signInDivRef = useRef(null);

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

  // Initialize Google Sign-in button
  useEffect(() => {
    if (!isAuthenticated && signInDivRef.current) {
      renderGoogleButton("signInDiv");
    }
  }, [isAuthenticated, renderGoogleButton]);

  return (
    <div className="mt-auto">
      {isAuthenticated ? (
        <button
          onClick={handleDownload}
          className="w-full bg-orange-700 text-white px-4 py-2 rounded-lg hover:bg-orange-800 flex items-center justify-center space-x-2"
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
          className="w-full px-4 py-2 rounded-lg flex items-center justify-center space-x-2"
        />
      )}
    </div>
  );
};
