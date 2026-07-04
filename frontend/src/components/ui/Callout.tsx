import type { ReactNode } from "react";
import type { CalloutVariant } from "./types";

export interface CalloutProps {
  variant?: CalloutVariant;
  title?: string;
  children: ReactNode;
  className?: string;
}

const variantConfig: Record<
  CalloutVariant,
  { icon: string; border: string; bg: string; title: string }
> = {
  info: {
    icon: "ℹ",
    border: "border-blue-bright/40",
    bg: "bg-blue-bright/10",
    title: "text-blue-bright",
  },
  warning: {
    icon: "⚠",
    border: "border-amber-500/40",
    bg: "bg-amber-500/10",
    title: "text-amber-500",
  },
  success: {
    icon: "✓",
    border: "border-emerald/40",
    bg: "bg-emerald/10",
    title: "text-emerald",
  },
};

export function Callout({
  variant = "info",
  title,
  children,
  className = "",
}: CalloutProps) {
  const config = variantConfig[variant];

  return (
    <div
      role="note"
      className={`rounded-md border p-4 ${config.border} ${config.bg} ${className}`}
      aria-label={title ?? `${variant} callout`}
    >
      <div className="flex gap-3">
        <span
          className={`flex h-6 w-6 shrink-0 items-center justify-center rounded-sm font-mono text-sm font-bold ${config.title}`}
          aria-hidden="true"
        >
          {config.icon}
        </span>
        <div className="min-w-0 flex-1">
          {title && (
            <p className={`font-heading text-sm font-semibold ${config.title}`}>
              {title}
            </p>
          )}
          <div
            className={`text-sm text-content-secondary leading-relaxed ${
              title ? "mt-1" : ""
            }`}
          >
            {children}
          </div>
        </div>
      </div>
    </div>
  );
}
