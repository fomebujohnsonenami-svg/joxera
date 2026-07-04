import type { ReactNode } from "react";

export interface RoleCardProps {
  role: string;
  title: string;
  description: string;
  icon?: ReactNode;
  ctaLabel?: string;
  onCtaClick?: () => void;
  ctaHref?: string;
  highlighted?: boolean;
  className?: string;
}

export function RoleCard({
  role,
  title,
  description,
  icon,
  ctaLabel,
  onCtaClick,
  ctaHref,
  highlighted = false,
  className = "",
}: RoleCardProps) {
  const borderClass = highlighted
    ? "border-accent/50 ring-1 ring-accent/20"
    : "border-border hover:border-blue-bright/30";

  return (
    <article
      className={`rounded-md border bg-surface-elevated p-6 transition-colors ${borderClass} ${className}`}
      aria-labelledby={`role-${role}-title`}
    >
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="font-mono text-[10px] font-bold uppercase tracking-widest text-content-muted mb-2">
            {role}
          </p>
          <h3
            id={`role-${role}-title`}
            className="font-heading text-xl font-semibold text-content-primary"
          >
            {title}
          </h3>
        </div>
        {icon && (
          <div
            className="flex h-10 w-10 shrink-0 items-center justify-center rounded-md bg-emerald/15 text-emerald"
            aria-hidden="true"
          >
            {icon}
          </div>
        )}
      </div>

      <p className="mt-3 text-sm text-content-secondary leading-relaxed">
        {description}
      </p>

      {ctaLabel && (ctaHref || onCtaClick) && (
        <div className="mt-5">
          {ctaHref ? (
            <a
              href={ctaHref}
              className="inline-flex items-center rounded-md bg-blue-bright px-4 py-2 text-sm font-semibold text-white hover:bg-blue-bright/90 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-bright"
            >
              {ctaLabel}
            </a>
          ) : (
            <button
              type="button"
              onClick={onCtaClick}
              className="inline-flex items-center rounded-md bg-blue-bright px-4 py-2 text-sm font-semibold text-white hover:bg-blue-bright/90 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-bright"
            >
              {ctaLabel}
            </button>
          )}
        </div>
      )}
    </article>
  );
}
