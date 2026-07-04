import { useState, type ReactNode } from "react";
import { Sidebar, type SidebarProps } from "./Sidebar";
import { TopBar, type TopBarProps } from "./TopBar";

export interface AppShellProps {
  topBar?: TopBarProps;
  sidebar: Omit<SidebarProps, "isOpen" | "onClose">;
  children: ReactNode;
  className?: string;
}

/**
 * Responsive shell: sidebar visible at 1024px+, drawer below.
 */
export function AppShell({
  topBar = {},
  sidebar,
  children,
  className = "",
}: AppShellProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className={`flex min-h-screen flex-col bg-surface-primary ${className}`}>
      <TopBar
        {...topBar}
        showMenuButton
        onMenuClick={() => setSidebarOpen(true)}
      />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar
          {...sidebar}
          isOpen={sidebarOpen}
          onClose={() => setSidebarOpen(false)}
        />
        <main
          id="main-content"
          className="flex-1 overflow-y-auto p-4 lg:p-6"
          tabIndex={-1}
        >
          {children}
        </main>
      </div>
    </div>
  );
}
