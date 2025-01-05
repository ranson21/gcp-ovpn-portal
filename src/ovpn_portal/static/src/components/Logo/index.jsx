import React from "react";

export const OpenVPNLogo = () => {
  return (
    <div className="flex items-center space-x-2 mb-8">
      <div className="h-8 flex items-center">
        <svg
          height="32"
          viewBox="0 0 540 80"
          className="h-full w-auto"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          {/* Shield background */}
          <path
            d="M28 72s32-16 32-40V12L28 0 0 12v20c0 24 28 40 28 40z"
            fill="#F78B1F" // OpenVPN orange
          />

          {/* Lock symbol */}
          <path
            d="M28 16c-4.4 0-8 3.6-8 8v4h-4v16h24V28h-4v-4c0-4.4-3.6-8-8-8zm0 4c2.2 0 4 1.8 4 4v4H24v-4c0-2.2 1.8-4 4-4z"
            fill="white"
          />

          {/* Text */}
          <text
            x="70"
            y="45"
            style={{
              fontFamily: "Arial, sans-serif",
              fontSize: "32px",
              fontWeight: "bold",
              fill: "#333333",
            }}
          >
            {`OpenVPN Client Portal (v${window.VERSION})`}
          </text>
        </svg>
      </div>
    </div>
  );
};
