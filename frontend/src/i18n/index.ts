import i18n from "i18next";
import LanguageDetector from "i18next-browser-languagedetector";
import { initReactI18next } from "react-i18next";
import { localeFromCountry } from "../utils/countries";

import en from "./locales/en.json";
import es from "./locales/es.json";
import fr from "./locales/fr.json";

const resources = {
  en: { translation: en },
  es: { translation: es },
  fr: { translation: fr },
};

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: "en",
    supportedLngs: ["en", "es", "fr"],
    interpolation: { escapeValue: false },
    detection: {
      order: ["localStorage", "navigator", "htmlTag"],
      caches: ["localStorage"],
    },
  });

/** Sync locale when user selects or navigates to a country route */
export function setLocaleFromCountry(countryCode: string): void {
  const locale = localeFromCountry(countryCode);
  if (i18n.language !== locale && locale in resources) {
    i18n.changeLanguage(locale);
  }
}

export default i18n;
