import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  type ReactNode,
} from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { setLocaleFromCountry } from "../i18n";
import { globalApi } from "../services/api/global";
import type { PaymentRail, RegionalConfig } from "../types";
import {
  clearStoredCountryOverride,
  getStoredCountryOverride,
  setStoredCountryOverride,
} from "../utils/currency";
import { normalizeCountryCode } from "../utils/countries";

export const LOCATION_QUERY_KEY = ["location", "regional-config"] as const;

interface LocationContextValue {
  /** Active ISO alpha-2 country code */
  currentCountry: string;
  countryName: string;
  localCurrency: string;
  payoutRail: PaymentRail;
  detectedVia: RegionalConfig["detected_via"];
  availableCountries: RegionalConfig["available_countries"];
  isLoading: boolean;
  isError: boolean;
  /** Override region (persisted to localStorage) */
  setCountry: (countryCode: string) => void;
  resetCountry: () => void;
}

const LocationContext = createContext<LocationContextValue | null>(null);

interface LocationProviderProps {
  children: ReactNode;
}

export function LocationProvider({ children }: LocationProviderProps) {
  const queryClient = useQueryClient();
  const storedOverride = getStoredCountryOverride();

  const configQuery = useQuery({
    queryKey: [...LOCATION_QUERY_KEY, storedOverride ?? "auto"],
    queryFn: () => globalApi.getRegionalConfig(storedOverride ?? undefined),
    staleTime: 5 * 60 * 1000,
    gcTime: 30 * 60 * 1000,
    retry: 2,
  });

  const config = configQuery.data;

  const setCountry = useCallback(
    (countryCode: string) => {
      const normalized = normalizeCountryCode(countryCode);
      setStoredCountryOverride(normalized);
      setLocaleFromCountry(normalized);
      queryClient.invalidateQueries({ queryKey: LOCATION_QUERY_KEY });
    },
    [queryClient]
  );

  const resetCountry = useCallback(() => {
    clearStoredCountryOverride();
    queryClient.invalidateQueries({ queryKey: LOCATION_QUERY_KEY });
  }, [queryClient]);

  const value = useMemo<LocationContextValue>(() => {
    const currentCountry = config?.country_code ?? storedOverride ?? "US";
    const detectedVia = storedOverride
      ? ("local" as const)
      : (config?.detected_via ?? "fallback");

    return {
      currentCountry,
      countryName: config?.country_name ?? currentCountry,
      localCurrency: config?.currency ?? "USD",
      payoutRail: (config?.payout_rail ?? "ACH") as PaymentRail,
      detectedVia,
      availableCountries: config?.available_countries ?? [],
      isLoading: configQuery.isLoading,
      isError: configQuery.isError,
      setCountry,
      resetCountry,
    };
  }, [
    config,
    configQuery.isLoading,
    configQuery.isError,
    storedOverride,
    setCountry,
    resetCountry,
  ]);

  useEffect(() => {
    if (config?.country_code) {
      setLocaleFromCountry(config.country_code);
    }
  }, [config?.country_code]);

  return (
    <LocationContext.Provider value={value}>{children}</LocationContext.Provider>
  );
}

export function useLocationContext(): LocationContextValue {
  const ctx = useContext(LocationContext);
  if (!ctx) {
    throw new Error("useLocationContext must be used within LocationProvider");
  }
  return ctx;
}

/** Convenience alias */
export const useLocation = useLocationContext;
