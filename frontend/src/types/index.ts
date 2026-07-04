export interface User {
  id: string;
  email: string;
  handle: string;
  country: string;
  isVerified: boolean;
  role: "talent" | "employer" | "both";
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterPayload {
  email: string;
  password: string;
  handle: string;
  country: string;
  role: "talent" | "employer";
}

export interface Job {
  id: string;
  title: string;
  description: string;
  country: string;
  field: string;
  tier: "standard" | "priority" | "enterprise";
  mode: "remote" | "onsite" | "hybrid";
  category: "tech" | "vocational" | "hybrid";
  compensation: string;
  compensationAmount?: number;
  compensationCurrency?: string;
  employerHandle: string;
  isVerifiedEmployer: boolean;
  distanceKm?: number;
  postedAt: string;
}

export interface JobFeedResponse {
  results: Job[];
  count: number;
  next: string | null;
  previous: string | null;
}

export interface PublicProfile {
  handle: string;
  displayName: string;
  country: string;
  isVerified: boolean;
  bio: string;
  credentials: ProofOfWorkCredential[];
  references: Reference[];
}

export interface ProofOfWorkCredential {
  id: string;
  jobTitle: string;
  field: string;
  tier: string;
  completedAt: string;
  signedBy: string;
  signatureHash: string;
  verifyUrl: string;
}

export interface Reference {
  id: string;
  author: string;
  text: string;
  rating: number;
}

export interface TalentDashboard {
  walletBalance: number;
  currency: string;
  activeMatches: number;
  references: Reference[];
  recentCredentials: ProofOfWorkCredential[];
}

export interface EmployerDashboard {
  activeJobs: number;
  escrowBalance: number;
  currency: string;
  recentHires: number;
  pendingApplications: number;
}

export interface WalletData {
  id: number;
  user: number;
  user_handle: string;
  currency: string;
  balance: string;
  rail: PaymentRail;
  updated_at: string;
}

export type TransactionType =
  | "credit"
  | "debit"
  | "escrow_lock"
  | "escrow_release"
  | "escrow_refund"
  | "payout";

export interface WalletTransaction {
  id: number;
  tx_type: TransactionType;
  amount: string;
  currency: string;
  balance_after: string;
  description: string;
  listing_title: string | null;
  metadata: Record<string, unknown>;
  created_at: string;
}

export type EscrowState = "pending" | "locked" | "released" | "refunded";

export interface EscrowStep {
  key: string;
  title: string;
  description: string;
  status: "pending" | "active" | "complete";
  at: string | null;
}

export interface EscrowTimeline {
  escrow_id: number;
  listing_title: string;
  amount: string;
  currency: string;
  state: EscrowState;
  employer_signed_off: boolean;
  talent_signed_off: boolean;
  funded_at: string | null;
  released_at: string | null;
  steps: EscrowStep[];
}

export interface EscrowRecord {
  id: number;
  listing: number;
  listing_title: string;
  employer: number;
  employer_handle: string;
  talent: number | null;
  talent_handle: string | null;
  amount: string;
  currency: string;
  state: EscrowState;
  provider: string;
  provider_ref: string;
  employer_signed_off: boolean;
  talent_signed_off: boolean;
  both_signed_off: boolean;
  funded_at: string | null;
  released_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface WalletDashboard {
  wallet: WalletData;
  transactions: WalletTransaction[];
  escrows: EscrowRecord[];
  escrow_timelines: EscrowTimeline[];
  locked_escrow_total: string;
}

export interface ReleaseEscrowResponse {
  escrow: EscrowRecord;
  released: boolean;
  timeline: EscrowStep[];
}

export type PaymentRail =
  | "MobileMoney"
  | "Pix"
  | "SEPA"
  | "ACH"
  | "UPI"
  | "SWIFT"
  | "Card";

export interface CountryConfigEntry {
  country_code: string;
  country_name: string;
  currency: string;
  payout_rail: string;
  default_payment_rail: string;
}

export interface RegionalConfig {
  country_code: string;
  country_name: string;
  currency: string;
  payout_rail: PaymentRail;
  detected_via: "geoip" | "header" | "fallback" | "query" | "local";
  available_countries: CountryConfigEntry[];
}
