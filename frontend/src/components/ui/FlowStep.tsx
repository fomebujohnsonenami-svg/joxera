import type { ReactNode } from "react";

export interface FlowStepProps {
  step: number;
  title: string;
  description: string;
  isLast?: boolean;
  status?: "pending" | "active" | "complete";
  className?: string;
}

const statusStyles = {
  pending: "border-border text-content-muted bg-surface-elevated",
  active: "border-accent text-accent bg-accent/10",
  complete: "border-emerald text-emerald bg-emerald/10",
};

export function FlowStep({
  step,
  title,
  description,
  isLast = false,
  status = "pending",
  className = "",
}: FlowStepProps) {
  return (
    <div className={`relative flex gap-4 ${className}`} role="listitem">
      {!isLast && (
        <div
          className="absolute left-[15px] top-8 bottom-0 w-px bg-border"
          aria-hidden="true"
        />
      )}

      <div
        className={`relative z-10 flex h-8 w-8 shrink-0 items-center justify-center rounded-full border-2 font-mono text-xs font-bold ${statusStyles[status]}`}
        aria-label={`Step ${step}`}
      >
        {status === "complete" ? "✓" : step}
      </div>

      <div className={`pb-8 ${isLast ? "pb-0" : ""}`}>
        <h4 className="font-heading text-sm font-semibold text-content-primary">
          {title}
        </h4>
        <p className="mt-1 text-sm text-content-secondary leading-relaxed">
          {description}
        </p>
      </div>
    </div>
  );
}

export interface FlowStepsProps {
  children: ReactNode;
  className?: string;
  "aria-label"?: string;
}

export function FlowSteps({
  children,
  className = "",
  "aria-label": ariaLabel = "Process steps",
}: FlowStepsProps) {
  return (
    <ol className={`space-y-0 ${className}`} role="list" aria-label={ariaLabel}>
      {children}
    </ol>
  );
}
