import apiClient from "./client";

export interface VerifyReferenceResult {
  valid: boolean;
  payload_hash?: string;
  payload?: Record<string, unknown>;
  public_key?: string;
  reference_id?: number;
  detail?: string;
}

export const referencesApi = {
  async verify(referenceId: string | number): Promise<VerifyReferenceResult> {
    const { data } = await apiClient.get(`/v3/global/references/verify/${referenceId}/`);
    return data;
  },

  async verifyByHash(hash: string): Promise<VerifyReferenceResult> {
    const { data } = await apiClient.get("/v3/global/references/verify/", {
      params: { hash },
    });
    return data;
  },
};
