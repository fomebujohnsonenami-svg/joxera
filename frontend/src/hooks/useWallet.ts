import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { paymentsApi } from "../services/api/payments";

export function useWalletDashboard() {
  return useQuery({
    queryKey: ["wallet-dashboard"],
    queryFn: () => paymentsApi.getWalletDashboard(),
  });
}

export function useReleaseEscrow() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (escrowId: number) => paymentsApi.releaseEscrow(escrowId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["wallet-dashboard"] });
    },
  });
}

export function useFundEscrowFromWallet() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (escrowId: number) => paymentsApi.fundEscrowFromWallet(escrowId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["wallet-dashboard"] });
    },
  });
}
