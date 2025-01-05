import React from "react";
import { VPNDrawer } from "./components/Drawer";
import { Instructions } from "./components/Instructions";
import { AuthProvider } from "./context/AuthContext";

export default function App() {
  return (
    <AuthProvider>
      <div className="flex min-h-screen bg-gray-50">
        <VPNDrawer />
        <main className="flex-1 p-8 ml-[333px]">
          <Instructions />
        </main>
      </div>
    </AuthProvider>
  );
}
