import React from "react";

export const AuthStatus = ({ isAuthenticated, email }) => {
  return (
    <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200 mb-6">
      <div className="text-sm font-medium text-gray-800 mb-2">
        Authentication
      </div>
      <div className="text-xs text-gray-600">
        {isAuthenticated ? `Signed in: ${email}` : "Not authenticated"}
      </div>
    </div>
  );
};
