import { Outlet } from "react-router-dom";
import { ConnectionBanner } from "../components/layout/ConnectionBanner";
import { Footer } from "../components/layout/Footer";
import { Header } from "../components/layout/Header";

export function RootLayout() {
  return (
    <div className="min-h-screen flex flex-col">
      <ConnectionBanner />
      <Header />
      <main className="flex-1">
        <Outlet />
      </main>
      <Footer />
    </div>
  );
}
