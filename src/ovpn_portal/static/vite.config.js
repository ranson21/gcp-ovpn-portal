import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { resolve } from "path";
import postcss from "postcss";
import tailwindcss from "tailwindcss";
import autoprefixer from "autoprefixer";
import fs from "fs";
import { build } from "vite";

// Custom plugin to copy index.html to dist
function copyIndexHtml() {
  return {
    name: "copy-index-html",
    closeBundle() {
      // Read the source index.html
      const source = fs.readFileSync(resolve(__dirname, "index.html"), "utf-8");

      // Ensure dist directory exists
      if (!fs.existsSync(resolve(__dirname, "dist"))) {
        fs.mkdirSync(resolve(__dirname, "dist"));
      }

      // Write to dist directory
      fs.writeFileSync(resolve(__dirname, "dist/index.html"), source);
    },
  };
}

function forceRebuild() {
  return {
    name: "force-rebuild",
    async handleHotUpdate({ file, server, modules, read }) {
      console.log("File changed - forcing rebuild:", file);

      try {
        // Create a clean config for the build
        const buildConfig = {
          root: server.config.root,
          base: server.config.base,
          mode: "development",
          build: {
            outDir: "dist",
            rollupOptions: {
              input: resolve(server.config.root, "src/main.jsx"),
            },
          },
          // Only include necessary plugins
          plugins: [
            server.config.plugins.find(
              (p) => p.name === "@vitejs/plugin-react"
            ),
          ],
        };

        await build(buildConfig);
        server.ws.send({ type: "full-reload" });
      } catch (error) {
        console.error("Build failed:", error);
      }
      return [];
    },
  };
}

export default defineConfig({
  root: __dirname, // Explicitly set the root
  plugins: [react(), copyIndexHtml(), forceRebuild(), postcss()],
  css: {
    postcss: {
      plugins: [tailwindcss(), autoprefixer()],
    },
  },
  build: {
    outDir: "dist",
    rollupOptions: {
      input: resolve(__dirname, "src/main.jsx"),
      output: {
        entryFileNames: "index.js",
        assetFileNames: "assets/[name].[ext]",
      },
    },
  },
  server: {
    watch: {
      // More aggressive watching
      usePolling: true,
      interval: 100,
      include: ["src/**"],
    },
    proxy: {
      "/auth": "http://localhost:8081",
      "/vpn": "http://localhost:8081",
      "/health": "http://localhost:8081",
    },
  },
});
