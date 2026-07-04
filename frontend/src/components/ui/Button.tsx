import { type ButtonHTMLAttributes } from "react";

type Variant = "primary" | "secondary" | "ghost";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  isLoading?: boolean;
}

const variants: Record<Variant, string> = {
  primary:
    "bg-blue-bright hover:bg-blue-bright/90 text-white font-semibold",
  secondary:
    "bg-surface-elevated hover:bg-surface-elevated/80 text-content-primary border border-border",
  ghost:
    "bg-transparent hover:bg-surface-elevated text-content-secondary hover:text-content-primary",
};

export function Button({
  variant = "primary",
  isLoading,
  className = "",
  children,
  disabled,
  ...props
}: ButtonProps) {
  return (
    <button
      className={`inline-flex items-center justify-center rounded-md px-4 py-2 text-sm transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-bright disabled:opacity-50 disabled:cursor-not-allowed ${variants[variant]} ${className}`}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading ? "…" : children}
    </button>
  );
}
