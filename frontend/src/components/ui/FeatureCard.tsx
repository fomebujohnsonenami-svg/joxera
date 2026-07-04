import type { ReactNode } from "react";

export interface FeatureCardProps {
  icon?: ReactNode;
  title: string;
  description: string;
  href?: string;
  className?: string;
}

export function FeatureCard({
  icon,
  title,
  description,
  href,
  className = "",
}: FeatureCardProps) {
  const content = (
    <>
      {icon && (
        <div
          className="mb-4 inline-flex h-10 w-10 items-center justify-center rounded-md bg-blue-bright/15 text-accent"
          aria-hidden="true"
        >
          {icon}
        </div>
      )}
      <h3 className="font-heading text-lg font-semibold text-content-primary">
        {title}
      </h3>
      <p className="mt-2 text-sm text-content-secondary leading-relaxed">
        {description}
      </p>
    </>
  );

  const baseClass = `rounded-md border border-border bg-surface-elevated p-5 transition-colors hover:border-blue-bright/30 ${className}`;

  if (href) {
    return (
      <a
        href={href}
        className={`block focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-bright ${baseClass}`}
      >
        {content}
      </a>
    );
  }

  return <article className={baseClass}>{content}</article>;
}
