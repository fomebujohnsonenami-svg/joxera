import type { PillVariant } from "./types";

export interface PillProps {
  variant: PillVariant;
  label?: string;
  className?: string;
}

const variantConfig: Record<
  PillVariant,
  { label: string; className: string }
> = {
  mvp: {
    label: "MVP",
    className: "border-emerald/40 bg-emerald/10 text-emerald",
  },
  v2: {
    label: "V2",
    className: "border-blue-bright/40 bg-blue-bright/10 text-blue-bright",
  },
  future: {
    label: "Future",
    className: "border-border bg-surface-elevated text-content-muted",
  },
};

export function Pill({ variant, label, className = "" }: PillProps) {
  const config = variantConfig[variant];

  return (
    <span
      className={`inline-flex items-center rounded-sm border px-2 py-0.5 font-mono text-[10px] font-bold uppercase tracking-wider ${config.className} ${className}`}
    >
      {label ?? config.label}
    </span>
  );
}
