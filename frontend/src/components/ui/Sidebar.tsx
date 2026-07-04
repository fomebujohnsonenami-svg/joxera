import { NavLink } from "react-router-dom";
import type { NavSection } from "./types";

export interface SidebarProps {
  sections: NavSection[];
  isOpen?: boolean;
  onClose?: () => void;
  footer?: React.ReactNode;
  className?: string;
}

export function Sidebar({
  sections,
  isOpen = false,
  onClose,
  footer,
  className = "",
}: SidebarProps) {
  const itemClass = ({ isActive }: { isActive: boolean }) =>
    `flex items-center gap-2.5 rounded-md px-3 py-2 text-sm transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-1 focus-visible:outline-blue-bright ${
      isActive
        ? "bg-blue-bright/15 text-accent font-medium"
        : "text-content-secondary hover:bg-surface-elevated hover:text-content-primary"
    }`;

  const panel = (
    <aside
      className={`flex h-full w-64 shrink-0 flex-col border-r border-border bg-surface-secondary ${className}`}
      aria-label="Sidebar navigation"
    >
      <div className="flex-1 overflow-y-auto px-3 py-4 space-y-6">
        {sections.map((section) => (
          <div key={section.id} role="group" aria-labelledby={`nav-${section.id}`}>
            <p
              id={`nav-${section.id}`}
              className="mb-2 px-3 font-mono text-[10px] font-bold uppercase tracking-widest text-content-muted"
            >
              {section.label}
            </p>
            <ul className="space-y-0.5" role="list">
              {section.items.map((item) => (
                <li key={item.id}>
                  {item.external ? (
                    <a
                      href={item.href}
                      className="flex items-center gap-2.5 rounded-md px-3 py-2 text-sm text-content-secondary hover:bg-surface-elevated hover:text-content-primary"
                      target="_blank"
                      rel="noopener noreferrer"
                      onClick={onClose}
                    >
                      {item.icon}
                      {item.label}
                    </a>
                  ) : (
                    <NavLink
                      to={item.href}
                      className={itemClass}
                      onClick={onClose}
                    >
                      {item.icon}
                      {item.label}
                    </NavLink>
                  )}
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
      {footer && (
        <div className="border-t border-border p-4 text-xs text-content-muted">
          {footer}
        </div>
      )}
    </aside>
  );

  return (
    <>
      {/* Desktop sidebar — visible at 1024px+ */}
      <div className="hidden sidebar:block h-full">{panel}</div>

      {/* Mobile drawer — below 1024px */}
      <div
        className={`sidebar:hidden fixed inset-0 z-50 transition-opacity ${
          isOpen ? "opacity-100 pointer-events-auto" : "opacity-0 pointer-events-none"
        }`}
        aria-hidden={!isOpen}
      >
        <button
          type="button"
          className="absolute inset-0 bg-black/60 backdrop-blur-sm"
          aria-label="Close navigation menu"
          onClick={onClose}
          tabIndex={isOpen ? 0 : -1}
        />
        <div
          className={`absolute inset-y-0 left-0 w-64 transform transition-transform duration-200 ease-out ${
            isOpen ? "translate-x-0" : "-translate-x-full"
          }`}
          role="dialog"
          aria-modal="true"
          aria-label="Navigation menu"
        >
          {panel}
        </div>
      </div>
    </>
  );
}
