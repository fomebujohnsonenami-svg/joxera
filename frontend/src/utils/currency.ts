const STORAGE_KEY = "joxera-country-override";

export function getStoredCountryOverride(): string | null {
  return localStorage.getItem(STORAGE_KEY);
}

export function setStoredCountryOverride(code: string): void {
  localStorage.setItem(STORAGE_KEY, code.toUpperCase());
}

export function clearStoredCountryOverride(): void {
  localStorage.removeItem(STORAGE_KEY);
}

/**
 * Format a numeric amount in the user's regional currency.
 * Falls back to plain string when amount is unavailable.
 */
export function formatRegionalPrice(
  job: {
    compensation: string;
    compensationAmount?: number;
    compensationCurrency?: string;
  },
  localCurrency: string,
  locale = "en"
): string {
  if (job.compensationAmount != null) {
    const currency = job.compensationCurrency ?? localCurrency;
    try {
      return new Intl.NumberFormat(locale, {
        style: "currency",
        currency,
        maximumFractionDigits: 0,
      }).format(job.compensationAmount);
    } catch {
      return `${currency} ${job.compensationAmount.toLocaleString(locale)}`;
    }
  }
  return job.compensation;
}
