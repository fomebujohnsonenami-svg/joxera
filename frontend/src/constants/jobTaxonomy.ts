/** Inclusive multi-tier job taxonomy — mirrors backend jobs/taxonomy.py */

export const JOB_FIELDS = [
  { value: "skilled_trades", label: "Skilled Trades" },
  { value: "technology", label: "Technology" },
  { value: "healthcare", label: "Healthcare" },
  { value: "logistics", label: "Logistics & Delivery" },
  { value: "hospitality", label: "Hospitality" },
  { value: "creative", label: "Creative & Design" },
  { value: "education", label: "Education & Training" },
  { value: "agriculture", label: "Agriculture" },
  { value: "community", label: "Community & Gig" },
  { value: "other", label: "Other" },
] as const;

export type JobField = (typeof JOB_FIELDS)[number]["value"];

export const JOB_MODES = [
  { value: "remote", label: "Remote" },
  { value: "onsite", label: "On-site" },
  { value: "hybrid", label: "Hybrid" },
] as const;

export type JobMode = (typeof JOB_MODES)[number]["value"];

export const JOB_TIERS = [
  { value: "standard", label: "Community", profile: "community" as const },
  { value: "priority", label: "Priority", profile: "community" as const },
  { value: "enterprise", label: "Enterprise", profile: "enterprise" as const },
] as const;

export type JobTier = (typeof JOB_TIERS)[number]["value"];

export const DEFAULT_RADIUS_KM = 15;
export const MIN_RADIUS_KM = 1;
export const MAX_RADIUS_KM = 100;

export function fieldToCategory(
  field: string
): "tech" | "vocational" | "hybrid" {
  if (field === "technology") return "tech";
  if (field === "skilled_trades" || field === "community" || field === "agriculture") {
    return "vocational";
  }
  return "hybrid";
}
