// src/ovpn_portal/static/src/components/Drawer/ConnectionDiagnostics.jsx
import React, { useState, useEffect } from "react";
import { StatusIndicator } from "../StatusIndicator";

export const ConnectionDiagnostics = ({ isConnected }) => {
  const [diagnostics, setDiagnostics] = useState({
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
  useEffect(() => {
    runDiagnostics();
    const interval = setInterval(runDiagnostics, 60000); // Run every minute
    return () => clearInterval(interval);
  }, [isConnected]);

  return (
    <div className="bg-white rounded-lg shadow-sm p-4 mb-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-medium text-gray-800">
          Connection Diagnostics
        </h3>
        {diagnostics.dns.status === "checking" ? (
          <div className="flex">
            <span className="text-xs text-blue-600 mr-2">Running Tests...</span>
            <div className="animate-spin rounded-full h-4 w-4 border-2 border-gray-300 border-t-gray-600" />
          </div>
        ) : (
          <button
            className="text-xs text-blue-600 hover:text-blue-800"
            onClick={runDiagnostics}
          >
            Run Tests
          </button>
        )}
      </div>

      {/* DNS Status */}
      <div className="mb-3">
        <StatusIndicator
          status={diagnostics.dns.status}
          text={`DNS Resolution: ${
            diagnostics.dns.status === "checking"
              ? "Checking..."
              : diagnostics.dns.status === "healthy"
              ? `Healthy (${diagnostics.dns.latency}ms)`
              : "Issues Detected"
          }`}
        />
      </div>

      {/* Connectivity Status */}
      <div className="mb-3">
        <StatusIndicator
          status={diagnostics.connectivity.status}
          text={`Connectivity: ${
            diagnostics.connectivity.status === "checking"
              ? "Checking..."
              : diagnostics.connectivity.status === "healthy"
              ? "All Services Reachable"
              : "Some Services Unreachable"
          }`}
        />
        {diagnostics.connectivity.details.map((detail, index) => (
          <div
            key={`detail-${index}`}
            className="ml-4 text-xs text-gray-500 mt-1"
          >
            {`${detail.name}: ${
              detail.status === "success" ? `${detail.latency}ms` : "Failed"
            }`}
          </div>
        ))}
      </div>

      {/* Stability Status */}
      <div className="mb-3">
        <StatusIndicator
          status={diagnostics.stability.status}
          text={`Connection Stability: ${
            diagnostics.stability.status === "checking"
              ? "Checking..."
              : diagnostics.stability.status === "stable"
              ? `Stable (avg ${diagnostics.stability.averageLatency}ms)`
              : diagnostics.stability.status === "unstable"
              ? "Minor Issues Detected"
              : "Unstable Connection"
          }`}
        />
        {diagnostics.stability.drops > 0 && (
          <div className="ml-4 text-xs text-gray-500 mt-1">
            {`Packet Loss: ${((diagnostics.stability.drops / 5) * 100).toFixed(
              1
            )}%`}
          </div>
        )}
      </div>
    </div>
  );
};
