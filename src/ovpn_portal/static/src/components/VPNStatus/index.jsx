import React, { Fragment } from "react";
import { useServerStatus } from "../../hooks/useServerStatus";

export const StatusCard = ({ pollingInterval }) => {
  const serverStatus = useServerStatus(pollingInterval);

  return (
    <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
      {/* Server Status Indicator */}
      <div className="flex items-center space-x-2 mb-4">
        <div
          className={`h-2 w-2 rounded-full ${
            serverStatus.loading
              ? "bg-gray-300"
              : serverStatus.isActive && serverStatus.isOperational
              ? "bg-green-500"
              : "bg-red-500"
          }`}
        />
        <span
          className={`text-sm font-medium ${
            serverStatus.loading
              ? "text-gray-500"
              : serverStatus.isActive && serverStatus.isOperational
              ? "text-green-700"
              : "text-red-700"
          }`}
        >
          {serverStatus.loading
            ? "Checking Status..."
            : serverStatus.isActive && serverStatus.isOperational
            ? "Server Active"
            : "Server Offline"}
        </span>
      </div>

      {/* Status Details */}
      <div className="flex items-center justify-between text-sm text-gray-600 border-t border-gray-100 pt-4">
        <span>Server Status</span>
        <div className="flex items-center space-x-1">
          {serverStatus.loading ? (
            <Fragment>
              <div className="animate-spin rounded-full h-4 w-4 border-2 border-gray-300 border-t-gray-600" />
              <span className="text-gray-600">Checking...</span>
            </Fragment>
          ) : (
            <Fragment>
              <svg
                className={`h-4 w-4 ${
                  serverStatus.isOperational ? "text-green-500" : "text-red-500"
                }`}
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
              >
                {serverStatus.isOperational ? (
                  <polyline points="20 6 9 17 4 12" />
                ) : (
                  <line x1="18" y1="6" x2="6" y2="18" />
                )}
              </svg>
              <span
                className={
                  serverStatus.isOperational ? "text-green-600" : "text-red-600"
                }
              >
                {serverStatus.isOperational ? "Operational" : "Offline"}
              </span>
            </Fragment>
          )}
        </div>
      </div>
    </div>
  );
};
