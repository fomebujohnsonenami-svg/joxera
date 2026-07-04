import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useLocationContext } from "../contexts/LocationProvider";
import { Button } from "../components/ui/Button";

const PILLARS = ["inclusive", "trust", "borderless", "credentials"] as const;

export function LandingPage() {
  const { t } = useTranslation();
  const { currentCountry, localCurrency, payoutRail, countryName } =
    useLocationContext();

  return (
    <div>
      <section className="max-w-6xl mx-auto px-4 py-20 text-center">
        <p className="text-joxera-400 text-sm font-semibold tracking-widest uppercase mb-4">
          {t("landing.tagline")}
        </p>
        <h1 className="text-4xl sm:text-6xl font-bold tracking-tight mb-6">
          {t("landing.title")}
        </h1>
        <p className="text-content-secondary text-lg max-w-2xl mx-auto leading-relaxed mb-4">
          {t("landing.subtitle")}
        </p>
        <p className="font-mono text-xs text-content-muted mb-10">
          {countryName} · {localCurrency} · {payoutRail}
        </p>
        <div className="flex flex-wrap gap-4 justify-center">
          <Link to={`/${currentCountry}/jobs`}>
            <Button>{t("landing.ctaBrowse")}</Button>
          </Link>
          <Link to="/auth/register">
            <Button variant="secondary">{t("landing.ctaRegister")}</Button>
          </Link>
        </div>
      </section>

      <section className="border-t border-slate-800 bg-slate-900/30">
        <div className="max-w-6xl mx-auto px-4 py-16 grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {PILLARS.map((key) => (
            <div
              key={key}
              className="rounded-xl border border-slate-800 p-6 bg-slate-950/50"
            >
              <h2 className="text-joxera-400 font-semibold mb-2">
                {t(`landing.pillars.${key}`)}
              </h2>
              <p className="text-sm text-slate-400 leading-relaxed">
                {t(`landing.pillarDescriptions.${key}`)}
              </p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
