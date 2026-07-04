import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { registerSW } from "virtual:pwa-register";
import App from "./App";
import { initTheme } from "./contexts/ThemeContext";
import { AppProviders } from "./providers/AppProviders";
import "./i18n";
import "./index.css";

initTheme();

registerSW({
  onOfflineReady() {
    console.info("[Joxera PWA] App ready for offline use.");
  },
  onRegisteredSW(_swUrl, registration) {
    registration &&
      setInterval(() => registration.update(), 60 * 60 * 1000);
  },
});

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <AppProviders>
      <App />
    </AppProviders>
  </StrictMode>
);
