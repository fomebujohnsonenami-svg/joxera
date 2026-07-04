import type { ReactNode } from "react";
import { Link, NavLink } from "react-router-dom";
import { ThemeToggle } from "./ThemeToggle";
import type { NavItem } from "./types";

function GlobeIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      viewBox="0 0 24 24"
      fill="none"
      aria-hidden="true"
    >
      <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="1.75" />
      <path
        d="M3 12h18M12 3c2.5 2.7 3.8 6.3 3.8 9s-1.3 6.3-3.8 9M12 3c-2.5 2.7-3.8 6.3-3.8 9s1.3 6.3 3.8 9"
        stroke="currentColor"
        strokeWidth="1.75"
      />
    </svg>
  );
}

function MenuIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path
        d="M4 7h16M4 12h16M4 17h16"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
      />
    </svg>
  );
}

export interface TopBarProps {
  brand?: ReactNode;
  brandHref?: string;
  navItems?: NavItem[];
  version?: string;
  onMenuClick?: () => void;
  showMenuButton?: boolean;
  className?: string;
}

export function TopBar({
  brand,
  brandHref = "/",
  navItems = [],
  version = "v0.1",
  onMenuClick,
  showMenuButton = false,
  className = "",
}: TopBarProps) {
  const navLinkClass = ({ isActive }: { isActive: boolean }) =>
    `text-sm font-medium transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-bright rounded-sm px-2 py-1 ${
      isActive
        ? "text-accent"
        : "text-content-secondary hover:text-content-primary"
    }`;

  return (
    <header
      className={`sticky top-0 z-40 border-b border-border bg-surface-secondary/90 backdrop-blur-md ${className}`}
      role="banner"
    >
      <div className="flex h-14 items-center gap-4 px-4 lg:px-6">
        {showMenuButton && (
          <button
            type="button"
            onClick={onMenuClick}
            className="sidebar:hidden inline-flex items-center justify-center rounded-md p-2 text-content-secondary hover:bg-surface-elevated hover:text-content-primary focus-visible:outline focus-visible:outline-2 focus-visible:outline-blue-bright"
            aria-label="Open navigation menu"
          >
            <MenuIcon className="h-5 w-5" />
          </button>
        )}

        <Link
          to={brandHref}
          className="flex items-center gap-2.5 font-heading font-bold text-lg tracking-tight focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-bright rounded-sm"
        >
          <span className="inline-flex h-8 w-8 items-center justify-center rounded-md bg-blue-bright/15 text-accent animate-[spin_12s_linear_infinite]">
            <GlobeIcon className="h-5 w-5" />
          </span>
          {brand ?? (
            <>
              <span className="text-accent">Global</span>
              <span className="text-content-primary">Jobs</span>
            </>
          )}
        </Link>

        {navItems.length > 0 && (
          <nav
            className="hidden md:flex flex-1 items-center gap-1 ml-4"
            aria-label="Primary"
          >
            {navItems.map((item) =>
              item.external ? (
                <a
                  key={item.id}
                  href={item.href}
                  className="text-sm font-medium text-content-secondary hover:text-content-primary px-2 py-1 rounded-sm"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  {item.label}
                </a>
              ) : (
                <NavLink key={item.id} to={item.href} className={navLinkClass}>
                  {item.label}
                </NavLink>
              )
            )}
          </nav>
        )}

        <div className="ml-auto flex items-center gap-2">
          <span
            className="hidden sm:inline-flex font-mono text-xs text-content-muted border border-border rounded-sm px-2 py-0.5"
            aria-label={`Version ${version}`}
          >
            {version}
          </span>
          <ThemeToggle />
        </div>
      </div>
    </header>
  );
}
