// src/ovpn_portal/static/src/components/Drawer/NetworkMetrics.jsx
import React, { useState, useEffect } from "react";
import { useVpnStatus } from "../../hooks/useVpnStatus";

export const NetworkMetrics = () => {
  const { connected, clientIp } = useVpnStatus();
  const [metrics, setMetrics] = useState({
    location: { city: "Loading...", country: "...", region: "" },
    latency: { value: null },
    connectionQuality: { status: "checking" },
  });

  // Helper function to determine connection quality based on latency
  const getConnectionQuality = (latency) => {
    if (!latency) return { status: "unknown", color: "gray" };
    if (latency < 50) return { status: "Excellent", color: "green" };
    if (latency < 100) return { status: "Good", color: "green" };
    if (latency < 200) return { status: "Fair", color: "yellow" };
    return { status: "Poor", color: "red" };
  };

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const start = performance.now();

        // Use GeoJS for location data (more generous rate limits)
        const locationResponse = await fetch(
          "https://get.geojs.io/v1/ip/geo.json"
        );
        if (!locationResponse.ok) {
          throw new Error("Location API request failed");
        }

        const locationData = await locationResponse.json();
        const latencyValue = Math.round(performance.now() - start);
        const quality = getConnectionQuality(latencyValue);

        setMetrics({
          location: {
            city: locationData.city,
            region: locationData.region,
            country: locationData.country,
            isp: locationData.organization_name,
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
        setMetrics((prev) => ({
          ...prev,
          location: {
            city: "Error loading",
            region: "Unknown",
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
  }, [connected]);

  return (
    <div className="bg-white rounded-lg shadow-sm p-4 mb-4">
      {/* Connection Status */}
      <div className="mb-4 border-b border-gray-100 pb-4">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-sm font-medium text-gray-800">
            Connection Status
          </h3>
          <span
            className={`px-2 py-1 text-xs rounded-full ${
              connected
                ? "bg-green-100 text-green-800"
                : "bg-gray-100 text-gray-800"
            }`}
          >
            {connected ? "Connected" : "Not Connected"}
          </span>
        </div>

        {/* Connection Quality */}
        {!metrics.connectionQuality.loading && (
          <div className="flex items-center mt-2 justify-between">
            <span className="text-sm text-gray-600 mr-2">
              Connection Quality:
            </span>
            <span
              className={`text-sm font-medium ${
                metrics.connectionQuality.color === "green"
                  ? "text-green-600"
                  : metrics.connectionQuality.color === "yellow"
                  ? "text-yellow-600"
                  : metrics.connectionQuality.color === "red"
                  ? "text-red-600"
                  : "text-gray-600"
              }`}
            >
              {metrics.connectionQuality.status}
            </span>
          </div>
        )}
      </div>

      {/* Connection Details */}
      <div className="space-y-3">
        {/* Current Location */}
        <div className="flex justify-between items-start text-sm">
          <span className="text-gray-600">Location:</span>
          <div className="text-right">
            <div className="font-medium">
              {metrics.location.loading
                ? "Loading..."
                : `${metrics.location.city}, ${metrics.location.region}`}
            </div>
            <div className="font-medium text-gray-500 text-xs">
              {metrics.location.loading
                ? "Loading..."
                : metrics.location.country}
            </div>
          </div>
        </div>

        {/* ISP Info */}
        <div className="flex justify-between items-center text-sm">
          <span className="text-gray-600">Network Provider:</span>
          <span className="font-medium text-right max-w-28">
            {metrics.location.loading
              ? "Loading..."
              : metrics.location.isp || "Unknown"}
          </span>
        </div>

        {/* IP Address */}
        <div className="flex justify-between items-center text-sm">
          <span className="text-gray-600">IP Address:</span>
          <span className="font-medium">{clientIp || "Unknown"}</span>
        </div>

        {/* Response Time */}
        <div className="flex justify-between items-center text-sm">
          <span className="text-gray-600">Response Time:</span>
          <span
            className={`font-medium ${
              metrics.latency.value < 100
                ? "text-green-600"
                : metrics.latency.value < 200
                ? "text-yellow-600"
                : "text-red-600"
            }`}
          >
            {metrics.latency.loading
              ? "Loading..."
              : `${metrics.latency.value}ms`}
          </span>
        </div>
      </div>
    </div>
  );
};
