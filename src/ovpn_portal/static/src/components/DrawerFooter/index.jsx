import React from "react";

export const DrawerFooter = ({ version = "v2.5.1" }) => {
  return (
    <div className="mt-6 text-center">
      <p className="text-xs text-gray-500">OpenVPN • {version}</p>
    </div>
  );
};
