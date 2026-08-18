import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],


  server: {
    port: 5173,

    // Proxy /api requests to FastAPI backend
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
      "/ws": {
        target: "ws://localhost:8000",
        ws: true,
      },
    },
  },

  // Force Vite to pre-bundle these packages so their internals are not
  // individually transformed (avoids react-router v7 .tsx source files
  // being picked up by the OXC JSX transform)
  optimizeDeps: {
    include: [
      "react",
      "react-dom",
      "react-dom/client",
      "react-router-dom",
      "axios",
    ],
    exclude: ["@tailwindcss/vite"],
  },
});
