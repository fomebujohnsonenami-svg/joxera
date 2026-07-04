import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { authApi } from "../services/api/auth";
import { tokenStorage } from "../services/auth/tokenStorage";
import type { LoginCredentials, RegisterPayload } from "../types";

export const AUTH_QUERY_KEY = ["auth", "me"] as const;

export function useAuth() {
  const queryClient = useQueryClient();

  const meQuery = useQuery({
    queryKey: AUTH_QUERY_KEY,
    queryFn: authApi.me,
    enabled: tokenStorage.hasTokens(),
    staleTime: 5 * 60 * 1000,
    retry: false,
  });

  const loginMutation = useMutation({
    mutationFn: (credentials: LoginCredentials) => authApi.login(credentials),
    onSuccess: (data) => {
      tokenStorage.setTokens(data.access, data.refresh);
      queryClient.setQueryData(AUTH_QUERY_KEY, data.user);
    },
  });

  const registerMutation = useMutation({
    mutationFn: (payload: RegisterPayload) => authApi.register(payload),
    onSuccess: (data) => {
      tokenStorage.setTokens(data.access, data.refresh);
      queryClient.setQueryData(AUTH_QUERY_KEY, data.user);
    },
  });

  const logoutMutation = useMutation({
    mutationFn: async () => {
      const refresh = tokenStorage.getRefresh();
      if (refresh) {
        await authApi.logout(refresh);
      }
    },
    onSettled: () => {
      tokenStorage.clear();
      queryClient.clear();
    },
  });

  const kycMutation = useMutation({
    mutationFn: authApi.startKyc,
  });

  return {
    user: meQuery.data ?? null,
    isAuthenticated: Boolean(meQuery.data),
    isLoading: meQuery.isLoading,
    login: loginMutation,
    register: registerMutation,
    logout: logoutMutation,
    startKyc: kycMutation,
  };
}
