import { useCallback, useEffect, useState } from "react";
import {
  DEFAULT_RADIUS_KM,
  JOB_FIELDS,
  JOB_MODES,
  MAX_RADIUS_KM,
  MIN_RADIUS_KM,
} from "../../constants/jobTaxonomy";
import { Button } from "../ui/Button";

export interface JobFeedFilters {
  field: string;
  mode: string;
  radiusKm: number;
  lat: number | null;
  lng: number | null;
}

export const DEFAULT_JOB_FEED_FILTERS: JobFeedFilters = {
  field: "",
  mode: "all",
  radiusKm: DEFAULT_RADIUS_KM,
  lat: null,
  lng: null,
};

interface JobFeedFilterProps {
  value: JobFeedFilters;
  onChange: (next: JobFeedFilters) => void;
  onApply?: () => void;
  className?: string;
}

export function JobFeedFilter({
  value,
  onChange,
  onApply,
  className = "",
}: JobFeedFilterProps) {
  const [geoError, setGeoError] = useState<string | null>(null);
  const [locating, setLocating] = useState(false);

  const requestLocation = useCallback(() => {
    if (!navigator.geolocation) {
      setGeoError("Geolocation is not supported in this browser.");
      return;
    }
    setLocating(true);
    setGeoError(null);
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        onChange({
          ...value,
          lat: pos.coords.latitude,
          lng: pos.coords.longitude,
        });
        setLocating(false);
      },
      () => {
        setGeoError("Could not access your location.");
        setLocating(false);
      },
      { enableHighAccuracy: true, timeout: 10000 }
    );
  }, [onChange, value]);

  useEffect(() => {
    if (value.lat == null && value.lng == null && value.mode !== "remote") {
      requestLocation();
    }
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const fieldLabel =
    JOB_FIELDS.find((f) => f.value === value.field)?.label ?? "All fields";
  const modeLabel =
    value.mode === "all"
      ? "All modes"
      : (JOB_MODES.find((m) => m.value === value.mode)?.label ?? value.mode);

  const showRadius = value.mode !== "remote";

  return (
    <section
      className={`rounded-lg border border-border bg-surface-elevated p-4 sm:p-5 space-y-5 ${className}`}
      aria-label="Job feed filters"
    >
      <div className="flex flex-wrap items-end gap-4">
        <FilterSelect
          label="Field"
          value={value.field}
          onChange={(field) => onChange({ ...value, field })}
          options={[{ value: "", label: "All fields" }, ...JOB_FIELDS]}
        />
        <FilterSelect
          label="Mode"
          value={value.mode}
          onChange={(mode) => onChange({ ...value, mode })}
          options={[
            { value: "all", label: "All modes" },
            ...JOB_MODES,
          ]}
        />
        {showRadius && (
          <div className="min-w-[140px] flex-1">
            <label className="block font-mono text-[10px] font-bold uppercase tracking-widest text-content-muted mb-1.5">
              Radius
            </label>
            <div className="flex items-center gap-2">
              <input
                type="range"
                min={MIN_RADIUS_KM}
                max={MAX_RADIUS_KM}
                value={value.radiusKm}
                onChange={(e) =>
                  onChange({ ...value, radiusKm: Number(e.target.value) })
                }
                className="flex-1 accent-accent"
                aria-valuetext={`${value.radiusKm} kilometers`}
              />
              <span className="font-mono text-sm text-accent w-14 text-right">
                {value.radiusKm} km
              </span>
            </div>
          </div>
        )}
      </div>

      {showRadius && (
        <div className="grid sm:grid-cols-[1fr_auto] gap-4 items-center">
          <RadiusMapPreview
            lat={value.lat}
            lng={value.lng}
            radiusKm={value.radiusKm}
          />
          <div className="space-y-2">
            <Button
              type="button"
              variant="secondary"
              onClick={requestLocation}
              isLoading={locating}
            >
              Use my location
            </Button>
            {geoError && (
              <p className="text-xs text-amber-400" role="alert">
                {geoError}
              </p>
            )}
            {value.lat != null && value.lng != null && (
              <p className="font-mono text-[10px] text-content-muted">
                {value.lat.toFixed(4)}, {value.lng.toFixed(4)}
              </p>
            )}
          </div>
        </div>
      )}

      <div className="flex flex-wrap items-center justify-between gap-3 pt-1 border-t border-border-subtle">
        <p className="text-sm text-content-secondary">
          <span className="text-content-primary font-medium">{fieldLabel}</span>
          <span className="mx-2 text-content-muted">·</span>
          <span>{modeLabel}</span>
          {showRadius && (
            <>
              <span className="mx-2 text-content-muted">·</span>
              <span className="font-mono text-accent">{value.radiusKm} KM</span>
            </>
          )}
        </p>
        {onApply && (
          <Button type="button" onClick={onApply}>
            Apply filters
          </Button>
        )}
      </div>
    </section>
  );
}

function FilterSelect({
  label,
  value,
  onChange,
  options,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  options: ReadonlyArray<{ value: string; label: string }>;
}) {
  return (
    <div className="min-w-[140px] flex-1 sm:flex-none">
      <label className="block font-mono text-[10px] font-bold uppercase tracking-widest text-content-muted mb-1.5">
        {label}
      </label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full rounded-md border border-border bg-surface-primary px-3 py-2 text-sm text-content-primary focus:outline-none focus:border-accent"
      >
        {options.map((opt) => (
          <option key={opt.value || "all"} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
    </div>
  );
}

/** Lightweight SVG map with search-radius circle — no external map SDK. */
function RadiusMapPreview({
  lat,
  lng,
  radiusKm,
}: {
  lat: number | null;
  lng: number | null;
  radiusKm: number;
}) {
  const cx = 120;
  const cy = 90;
  const r = Math.min(70, 12 + radiusKm * 2.2);

  return (
    <div
      className="relative rounded-md border border-border bg-blue-deep/40 overflow-hidden h-44"
      role="img"
      aria-label={`Map preview with ${radiusKm} km search radius`}
    >
      <svg viewBox="0 0 240 180" className="w-full h-full" aria-hidden="true">
        <defs>
          <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
            <path
              d="M 20 0 L 0 0 0 20"
              fill="none"
              stroke="rgba(6,182,212,0.15)"
              strokeWidth="0.5"
            />
          </pattern>
        </defs>
        <rect width="240" height="180" fill="url(#grid)" />
        <circle
          cx={cx}
          cy={cy}
          r={r}
          fill="rgba(6,182,212,0.12)"
          stroke="rgba(6,182,212,0.5)"
          strokeWidth="1.5"
          strokeDasharray="4 3"
        />
        <circle cx={cx} cy={cy} r="5" fill="#06b6d4" />
        <circle cx={cx} cy={cy} r="9" fill="none" stroke="#3b82f6" strokeWidth="1.5" />
      </svg>
      <div className="absolute bottom-2 left-2 right-2 flex justify-between text-[10px] font-mono text-content-muted px-1">
        <span>{lat != null ? `${lat.toFixed(2)}°N` : "—"}</span>
        <span>{lng != null ? `${lng.toFixed(2)}°E` : "Set location"}</span>
      </div>
    </div>
  );
}
