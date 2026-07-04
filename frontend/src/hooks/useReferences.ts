import { useQuery } from "@tanstack/react-query";
import { referencesApi } from "../services/api/references";

export function useVerifyReference(referenceId: string | null) {
  return useQuery({
    queryKey: ["verify-reference", referenceId],
    queryFn: () => referencesApi.verify(referenceId!),
    enabled: Boolean(referenceId),
    staleTime: Infinity,
  });
}
