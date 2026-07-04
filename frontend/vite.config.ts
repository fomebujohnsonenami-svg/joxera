import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { VitePWA } from "vite-plugin-pwa";

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: "autoUpdate",
      includeAssets: ["vite.svg"],
      manifest: {
        name: "Joxera",
        short_name: "Joxera",
        description:
          "Borderless employment marketplace — tech contracts and local gigs",
        theme_color: "#14b8a6",
        background_color: "#020617",
        display: "standalone",
        start_url: "/",
        icons: [
          {
            src: "/vite.svg",
            sizes: "192x192",
            type: "image/svg+xml",
          },
          {
            src: "/vite.svg",
            sizes: "512x512",
            type: "image/svg+xml",
          },
        ],
      },
      workbox: {
        globPatterns: ["**/*.{js,css,html,ico,png,svg,woff2}"],
        runtimeCaching: [
          {
            urlPattern: /^https?:\/\/.*\/api\/.*\/jobs.*/i,
            handler: "StaleWhileRevalidate",
            options: {
              cacheName: "joxera-job-feed",
              expiration: {
                maxEntries: 100,
                maxAgeSeconds: 60 * 60 * 24,
              },
              cacheableResponse: {
                statuses: [0, 200],
              },
            },
          },
          {
            urlPattern: /^https?:\/\/.*\/api\/health\/?$/i,
            handler: "NetworkFirst",
            options: {
              cacheName: "joxera-health",
              networkTimeoutSeconds: 5,
            },
          },
        ],
      },
      devOptions: {
        enabled: true,
      },
    }),
  ],
  server: {
    host: "0.0.0.0",
    port: 3000,
    allowedHosts: true,
    hmr: {
      clientPort: 443,
    },
    watch: {
      usePolling: true,
    },
  },
});
