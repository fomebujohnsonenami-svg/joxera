import type { ReactNode } from "react";

export interface MetricBoxProps {
  label: string;
  value: string | number;
  hint?: string;
  trend?: {
    direction: "up" | "down" | "neutral";
    label: string;
  };
  icon?: ReactNode;
  className?: string;
}

const trendColors = {
  up: "text-emerald",
  down: "text-red-400",
  neutral: "text-content-muted",
};

export function MetricBox({
  label,
  value,
  hint,
  trend,
  icon,
  className = "",
}: MetricBoxProps) {
  return (
    <article
      className={`rounded-md border border-border bg-surface-elevated p-5 ${className}`}
      aria-label={label}
    >
      <div className="flex items-start justify-between gap-3">
        <p className="font-mono text-[10px] font-bold uppercase tracking-widest text-content-muted">
          {label}
        </p>
        {icon && (
          <div className="text-accent" aria-hidden="true">
            {icon}
          </div>
        )}
      </div>

      <p className="mt-2 font-heading text-2xl sm:text-3xl font-bold text-content-primary tabular-nums">
        {value}
      </p>

      {(hint || trend) && (
        <div className="mt-2 flex flex-wrap items-center gap-2 text-xs">
          {trend && (
            <span className={`font-mono font-medium ${trendColors[trend.direction]}`}>
              {trend.direction === "up" && "↑ "}
              {trend.direction === "down" && "↓ "}
              {trend.label}
            </span>
          )}
          {hint && <span className="text-content-muted">{hint}</span>}
        </div>
      )}
    </article>
  );
}
