import React from "react";

export const StatusIndicator = ({ status, text }) => {
  const getStatusColor = (status) => {
    const colors = {
      connected: "bg-green-500",
      disconnected: "bg-red-500",
      checking: "bg-blue-500 animate-pulse",
      warning: "bg-yellow-500",
    };
    return colors[status] || "bg-gray-500";
  };

  return (
    <div className="flex items-center space-x-2">
      <div className={`h-2 w-2 rounded-full ${getStatusColor(status)}`} />
      {text && <span className="text-sm">{text}</span>}
    </div>
  );
};
