import {
  countryCodeToFlag,
  getCountryName,
  normalizeCountryCode,
} from "../../utils/countries";

export interface CountryBadgeProps {
  countryCode: string;
  verified?: boolean;
  showName?: boolean;
  size?: "sm" | "md";
  className?: string;
}

export function CountryBadge({
  countryCode,
  verified = true,
  showName = false,
  size = "md",
  className = "",
}: CountryBadgeProps) {
  const code = normalizeCountryCode(countryCode);
  const flag = countryCodeToFlag(code);
  const name = getCountryName(code);
  const sizeClass =
    size === "sm" ? "text-xs px-2 py-0.5 gap-1.5" : "text-sm px-2.5 py-1 gap-2";

  return (
    <span
      className={`inline-flex items-center rounded-sm border font-medium ${
        verified
          ? "border-emerald/30 bg-emerald/10 text-emerald"
          : "border-border bg-surface-elevated text-content-secondary"
      } ${sizeClass} ${className}`}
      title={showName ? undefined : name}
      aria-label={`${name}${verified ? ", verified" : ""}`}
    >
      <span className="text-base leading-none" aria-hidden="true">
        {flag}
      </span>
      <span className="font-mono font-bold tracking-wide">
        {code}
        {verified && " Verified"}
      </span>
      {showName && (
        <>
          <span className="text-content-muted" aria-hidden="true">
            ·
          </span>
          <span className="font-sans font-normal text-content-secondary">
            {name}
          </span>
        </>
      )}
    </span>
  );
}
