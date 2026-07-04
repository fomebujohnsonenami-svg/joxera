import apiClient from "./client";
import type { ReleaseEscrowResponse, WalletDashboard } from "../../types";

export const paymentsApi = {
  async getWalletDashboard(): Promise<WalletDashboard> {
    const { data } = await apiClient.get("/v3/global/payments/wallet/");
    return data;
  },

  async releaseEscrow(escrowId: number): Promise<ReleaseEscrowResponse> {
    const { data } = await apiClient.post("/v3/global/payments/release-escrow/", {
      escrow_id: escrowId,
    });
    return data;
  },

  async fundEscrowFromWallet(escrowId: number): Promise<{ escrow: ReleaseEscrowResponse["escrow"] }> {
    const { data } = await apiClient.post("/v3/global/payments/escrow/fund/", {
      escrow_id: escrowId,
      use_wallet: true,
    });
    return data;
  },
};
