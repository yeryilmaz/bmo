import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Proxy API requests to the FastAPI backend during development.
// This avoids CORS issues when running both servers locally.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
