/** ISO 3166-1 alpha-2 country codes supported by Joxera */
export const ISO_COUNTRIES: Record<string, string> = {
  US: "United States",
  GB: "United Kingdom",
  CA: "Canada",
  DE: "Germany",
  FR: "France",
  NG: "Nigeria",
  KE: "Kenya",
  IN: "India",
  BR: "Brazil",
  MX: "Mexico",
  AU: "Australia",
  JP: "Japan",
  ZA: "South Africa",
  GH: "Ghana",
  PH: "Philippines",
};

export function isValidCountryCode(code: string): boolean {
  return /^[A-Z]{2}$/.test(code.toUpperCase()) && code.toUpperCase() in ISO_COUNTRIES;
}

export function normalizeCountryCode(code: string): string {
  return code.toUpperCase();
}

/** Convert ISO 3166-1 alpha-2 code to flag emoji */
export function countryCodeToFlag(code: string): string {
  const normalized = normalizeCountryCode(code);
  if (!/^[A-Z]{2}$/.test(normalized)) return "🏳️";
  return String.fromCodePoint(
    ...normalized.split("").map((char) => 0x1f1e6 - 65 + char.charCodeAt(0))
  );
}

export function getCountryName(code: string): string {
  return ISO_COUNTRIES[normalizeCountryCode(code)] ?? code;
}

/** Map country code to preferred locale for i18n auto-detection */
export const COUNTRY_LOCALE_MAP: Record<string, string> = {
  US: "en",
  GB: "en",
  CA: "en",
  AU: "en",
  NG: "en",
  KE: "en",
  GH: "en",
  ZA: "en",
  PH: "en",
  IN: "en",
  DE: "de",
  FR: "fr",
  MX: "es",
  BR: "pt",
  JP: "ja",
};

export function localeFromCountry(countryCode: string): string {
  return COUNTRY_LOCALE_MAP[normalizeCountryCode(countryCode)] ?? "en";
}
