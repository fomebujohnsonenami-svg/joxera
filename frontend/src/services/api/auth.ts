import apiClient from "./client";
import type {
  AuthTokens,
  LoginCredentials,
  RegisterPayload,
  User,
} from "../../types";

export const authApi = {
  async login(credentials: LoginCredentials): Promise<AuthTokens & { user: User }> {
    const { data } = await apiClient.post("/auth/login/", credentials);
    return data;
  },

  async register(payload: RegisterPayload): Promise<AuthTokens & { user: User }> {
    const { data } = await apiClient.post("/auth/register/", payload);
    return data;
  },

  async me(): Promise<User> {
    const { data } = await apiClient.get("/auth/me/");
    return data;
  },

  async logout(refresh: string): Promise<void> {
    await apiClient.post("/auth/logout/", { refresh });
  },

  async startKyc(): Promise<{ redirectUrl: string }> {
    const { data } = await apiClient.post("/auth/kyc/start/");
    return data;
  },
};
