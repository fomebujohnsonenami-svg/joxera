import type { ReactNode } from "react";
import type { TagChip } from "./types";

export interface HeroProps {
  eyebrow?: string;
  title: ReactNode;
  subtitle?: ReactNode;
  tags?: TagChip[];
  actions?: ReactNode;
  className?: string;
}

export function Hero({
  eyebrow,
  title,
  subtitle,
  tags = [],
  actions,
  className = "",
}: HeroProps) {
  return (
    <section
      className={`relative overflow-hidden rounded-lg border border-border hero-gradient ${className}`}
      aria-labelledby="hero-title"
    >
      <div
        className="absolute inset-0 grid-pattern opacity-40 pointer-events-none"
        aria-hidden="true"
      />
      <div className="absolute inset-0 bg-gradient-to-t from-surface-primary/80 to-transparent pointer-events-none" aria-hidden="true" />

      <div className="relative px-6 py-12 sm:px-10 sm:py-16 lg:py-20">
        {eyebrow && (
          <p className="font-mono text-xs font-bold uppercase tracking-widest text-accent mb-4">
            {eyebrow}
          </p>
        )}

        <h1
          id="hero-title"
          className="font-heading text-3xl sm:text-4xl lg:text-5xl font-bold tracking-tight text-content-primary max-w-3xl"
        >
          {title}
        </h1>

        {subtitle && (
          <p className="mt-4 text-base sm:text-lg text-content-secondary max-w-2xl leading-relaxed">
            {subtitle}
          </p>
        )}

        {tags.length > 0 && (
          <ul className="mt-6 flex flex-wrap gap-2" role="list" aria-label="Tags">
            {tags.map((tag) => (
              <li key={tag.id}>
                <span className="inline-flex items-center rounded-sm border border-border bg-surface-elevated/60 px-3 py-1 text-xs font-medium text-content-secondary backdrop-blur-sm">
                  {tag.label}
                </span>
              </li>
            ))}
          </ul>
        )}

        {actions && (
          <div className="mt-8 flex flex-wrap items-center gap-3">{actions}</div>
        )}
      </div>
    </section>
  );
}
