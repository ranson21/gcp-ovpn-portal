import React from "react";

export const InstructionCard = ({ title, children }) => (
  <div className="instruction-card">
    <h3>{title}</h3>
    {children}
  </div>
);
