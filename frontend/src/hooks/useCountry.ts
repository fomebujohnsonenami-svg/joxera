import { useParams } from "react-router-dom";
import { useEffect } from "react";
import { useLocationContext } from "../contexts/LocationProvider";
import { setLocaleFromCountry } from "../i18n";
import {
  getCountryName,
  isValidCountryCode,
  normalizeCountryCode,
} from "../utils/countries";

/**
 * Resolves the effective country for the current view.
 * Route param (`/:country/...`) takes precedence over GeoIP/regional config.
 */
export function useCountry() {
  const { country: rawRouteCountry } = useParams<{ country: string }>();
  const { currentCountry, countryName: regionalName, localCurrency, payoutRail } =
    useLocationContext();

  const routeCountry = rawRouteCountry
    ? normalizeCountryCode(rawRouteCountry)
    : null;
  const routeValid = routeCountry ? isValidCountryCode(routeCountry) : false;

  const country = routeValid ? routeCountry! : currentCountry;
  const countryName = routeValid
    ? getCountryName(routeCountry!)
    : regionalName;
  const isValid = isValidCountryCode(country);
  const isRouteOverride = routeValid && routeCountry !== currentCountry;

  useEffect(() => {
    if (country && isValid) {
      setLocaleFromCountry(country);
    }
  }, [country, isValid]);

  return {
    country,
    countryName,
    isValid,
    isRouteOverride,
    localCurrency,
    payoutRail,
    /** Country from GeoIP / user preference (ignoring route) */
    regionalCountry: currentCountry,
  };
}
