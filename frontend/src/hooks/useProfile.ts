import { useQuery } from "@tanstack/react-query";
import { profileApi } from "../services/api/profile";

export const profileKeys = {
  public: (handle: string) => ["profile", handle] as const,
  talentDashboard: ["dashboard", "talent"] as const,
  employerDashboard: ["dashboard", "employer"] as const,
};

export function usePublicProfile(handle: string) {
  return useQuery({
    queryKey: profileKeys.public(handle),
    queryFn: () => profileApi.getPublicProfile(handle),
    staleTime: 2 * 60 * 1000,
    enabled: Boolean(handle),
  });
}

export function useTalentDashboard() {
  return useQuery({
    queryKey: profileKeys.talentDashboard,
    queryFn: profileApi.getTalentDashboard,
    staleTime: 30 * 1000,
  });
}

export function useEmployerDashboard() {
  return useQuery({
    queryKey: profileKeys.employerDashboard,
    queryFn: profileApi.getEmployerDashboard,
    staleTime: 30 * 1000,
  });
}
