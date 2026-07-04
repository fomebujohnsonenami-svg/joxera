import apiClient from "./client";
import type { RegionalConfig } from "../../types";

export const globalApi = {
  async getRegionalConfig(country?: string): Promise<RegionalConfig> {
    const { data } = await apiClient.get("/v3/global/config/", {
      params: country ? { country } : undefined,
    });
    return data;
  },
};
