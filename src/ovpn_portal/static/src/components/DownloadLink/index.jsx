import React from "react";

export const DownloadLink = ({ href, children }) => (
  <a href={href} className="download-link">
    {children}
  </a>
);
