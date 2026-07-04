import { FormEvent, useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import {
  JOB_FIELDS,
  JOB_MODES,
  JOB_TIERS,
  type JobField,
  type JobMode,
  type JobTier,
} from "../../constants/jobTaxonomy";
import { useLocationContext } from "../../contexts/LocationProvider";
import { jobsApi, type CreateListingPayload } from "../../services/api/jobs";
import { Button } from "../ui/Button";
import { Callout } from "../ui/Callout";
import { Pill } from "../ui/Pill";

export function PostJobForm() {
  const navigate = useNavigate();
  const { currentCountry, localCurrency } = useLocationContext();

  const [tier, setTier] = useState<JobTier>("standard");
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [field, setField] = useState<JobField>("skilled_trades");
  const [mode, setMode] = useState<JobMode>("onsite");
  const [budget, setBudget] = useState("");
  const [escrowId, setEscrowId] = useState("");
  const [lat, setLat] = useState<number | null>(null);
  const [lng, setLng] = useState<number | null>(null);

  const isEnterprise = tier === "enterprise";

  const createMutation = useMutation({
    mutationFn: (payload: CreateListingPayload) => jobsApi.createListing(payload),
    onSuccess: (job) => {
      navigate(`/${job.country}/jobs/${job.id}`);
    },
  });

  function captureLocation() {
    navigator.geolocation?.getCurrentPosition((pos) => {
      setLat(pos.coords.latitude);
      setLng(pos.coords.longitude);
    });
  }

  function handleSubmit(e: FormEvent) {
    e.preventDefault();

    const payload: CreateListingPayload = {
      title,
      description,
      field,
      tier,
      mode,
      country_code: currentCountry,
      currency: localCurrency,
      budget: parseFloat(budget),
      escrow_id: isEnterprise ? escrowId : "",
    };

    if (mode !== "remote" && lat != null && lng != null) {
      payload.geo_point = {
        type: "Point",
        coordinates: [lng, lat],
      };
    }

    createMutation.mutate(payload);
  }

  return (
    <form onSubmit={handleSubmit} className="max-w-2xl space-y-6">
      <header>
        <h1 className="text-2xl font-bold text-content-primary">Post a job</h1>
        <p className="text-content-secondary text-sm mt-1">
          Forms adapt for enterprise contracts vs. local community requests.
        </p>
      </header>

      <fieldset className="space-y-3">
        <legend className="font-mono text-[10px] font-bold uppercase tracking-widest text-content-muted">
          Posting tier
        </legend>
        <div className="grid sm:grid-cols-3 gap-3">
          {JOB_TIERS.map((t) => (
            <label
              key={t.value}
              className={`cursor-pointer rounded-md border p-4 transition-colors ${
                tier === t.value
                  ? "border-accent bg-accent/10"
                  : "border-border hover:border-blue-bright/30"
              }`}
            >
              <input
                type="radio"
                name="tier"
                value={t.value}
                checked={tier === t.value}
                onChange={() => setTier(t.value)}
                className="sr-only"
              />
              <div className="flex items-center justify-between mb-1">
                <span className="font-semibold text-sm">{t.label}</span>
                <Pill
                  variant={t.value === "enterprise" ? "v2" : "mvp"}
                  label={t.profile}
                />
              </div>
              <p className="text-xs text-content-muted">
                {t.profile === "enterprise"
                  ? "Escrow, compliance fields, hybrid/remote."
                  : "Quick community & trade gigs."}
              </p>
            </label>
          ))}
        </div>
      </fieldset>

      {isEnterprise ? (
        <Callout variant="info" title="Enterprise posting">
          Includes escrow reference, detailed scope, and multi-mode support for
          corporate contracts.
        </Callout>
      ) : (
        <Callout variant="success" title="Community posting">
          Optimized for local skilled trades and fast-turnaround neighborhood
          requests.
        </Callout>
      )}

      <div className="grid sm:grid-cols-2 gap-4">
        <FormField label="Title" required>
          <input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
            placeholder={
              isEnterprise ? "Senior backend engineer — 6 mo contract" : "Fix kitchen sink leak"
            }
            className={inputClass}
          />
        </FormField>
        <FormField label="Field" required>
          <select
            value={field}
            onChange={(e) => setField(e.target.value as JobField)}
            className={inputClass}
          >
            {JOB_FIELDS.map((f) => (
              <option key={f.value} value={f.value}>
                {f.label}
              </option>
            ))}
          </select>
        </FormField>
      </div>

      <FormField
        label="Description"
        required
        hint={isEnterprise ? "Include deliverables, timeline, compliance needs." : "Describe the task and access instructions."}
      >
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          required
          rows={isEnterprise ? 6 : 4}
          className={inputClass}
        />
      </FormField>

      <div className="grid sm:grid-cols-3 gap-4">
        <FormField label="Mode" required>
          <select
            value={mode}
            onChange={(e) => setMode(e.target.value as JobMode)}
            className={inputClass}
          >
            {JOB_MODES.map((m) => (
              <option key={m.value} value={m.value}>
                {m.label}
              </option>
            ))}
          </select>
        </FormField>
        <FormField label={`Budget (${localCurrency})`} required>
          <input
            type="number"
            min="1"
            step="0.01"
            value={budget}
            onChange={(e) => setBudget(e.target.value)}
            required
            className={inputClass}
          />
        </FormField>
        <FormField label="Country">
          <input
            value={currentCountry}
            readOnly
            className={`${inputClass} opacity-70`}
          />
        </FormField>
      </div>

      {isEnterprise && (
        <FormField label="Escrow ID" hint="Links to locked escrow for this contract.">
          <input
            value={escrowId}
            onChange={(e) => setEscrowId(e.target.value)}
            placeholder="esc_..."
            className={inputClass}
          />
        </FormField>
      )}

      {mode !== "remote" && (
        <div className="rounded-md border border-border p-4 space-y-3">
          <p className="text-sm font-medium">Job location (required for on-site/hybrid)</p>
          <Button type="button" variant="secondary" onClick={captureLocation}>
            Pin current location
          </Button>
          {lat != null && lng != null && (
            <p className="font-mono text-xs text-content-muted">
              {lat.toFixed(5)}, {lng.toFixed(5)}
            </p>
          )}
        </div>
      )}

      {createMutation.isError && (
        <Callout variant="warning" title="Could not publish">
          Verify your identity (KYC) before posting listings.
        </Callout>
      )}

      <Button type="submit" isLoading={createMutation.isPending} className="w-full sm:w-auto">
        {isEnterprise ? "Publish enterprise listing" : "Post community request"}
      </Button>
    </form>
  );
}

function FormField({
  label,
  hint,
  required,
  children,
}: {
  label: string;
  hint?: string;
  required?: boolean;
  children: React.ReactNode;
}) {
  return (
    <div>
      <label className="block text-sm text-content-secondary mb-1.5">
        {label}
        {required && <span className="text-accent ml-0.5">*</span>}
      </label>
      {children}
      {hint && <p className="text-xs text-content-muted mt-1">{hint}</p>}
    </div>
  );
}

const inputClass =
  "w-full rounded-md border border-border bg-surface-primary px-3 py-2 text-sm text-content-primary focus:outline-none focus:border-accent";
