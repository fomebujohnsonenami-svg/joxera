import apiClient from "./client";
import type { ProofOfWorkCredential, PublicProfile } from "../../types";

interface ApiCredential {
  id: number;
  job_title: string;
  field: string;
  tier: string;
  completed_at: string;
  signed_by: string;
  signature_hash: string;
  verify_url: string;
}

interface ApiPublicProfile {
  handle: string;
  display_name: string;
  country: string;
  is_verified: boolean;
  bio: string;
  credentials: ApiCredential[];
  references: unknown[];
}

function mapCredential(c: ApiCredential): ProofOfWorkCredential {
  return {
    id: String(c.id),
    jobTitle: c.job_title,
    field: c.field,
    tier: c.tier,
    completedAt: c.completed_at,
    signedBy: c.signed_by,
    signatureHash: c.signature_hash,
    verifyUrl: c.verify_url,
  };
}

export const profileApi = {
  async getPublicProfile(handle: string): Promise<PublicProfile> {
    const { data } = await apiClient.get<ApiPublicProfile>(`/profiles/${handle}/`);
    return {
      handle: data.handle,
      displayName: data.display_name,
      country: data.country,
      isVerified: data.is_verified,
      bio: data.bio,
      credentials: data.credentials.map(mapCredential),
      references: [],
    };
  },

  async getTalentDashboard(): Promise<import("../../types").TalentDashboard> {
    const { data } = await apiClient.get("/dashboard/talent/");
    return data;
  },

  async getEmployerDashboard(): Promise<import("../../types").EmployerDashboard> {
    const { data } = await apiClient.get("/dashboard/employer/");
    return data;
  },
};
