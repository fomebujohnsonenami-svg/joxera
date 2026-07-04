interface BadgeProps {
  children: React.ReactNode;
  variant?: "default" | "success" | "warning";
}

const variants = {
  default: "bg-surface-elevated text-content-secondary border border-border",
  success: "bg-emerald/10 text-emerald border border-emerald/30",
  warning: "bg-amber-500/10 text-amber-500 border border-amber-500/30",
};

export function Badge({ children, variant = "default" }: BadgeProps) {
  return (
    <span
      className={`inline-flex items-center rounded-sm px-2.5 py-0.5 text-xs font-medium ${variants[variant]}`}
    >
      {children}
    </span>
  );
}
