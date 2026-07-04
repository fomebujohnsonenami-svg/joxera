import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { ShieldCheck, Globe2, Award, Sparkles, ArrowRight } from "lucide-react";
import { useLocationContext } from "../contexts/LocationProvider";
import { Button } from "../components/ui/Button";

const HERO_IMG =
  "https://images.pexels.com/photos/5439474/pexels-photo-5439474.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940";

const PILLARS = [
  {
    key: "inclusive",
    Icon: Sparkles,
    tint: "var(--color-coral)",
    img: "https://images.pexels.com/photos/7491017/pexels-photo-7491017.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
  },
  {
    key: "trust",
    Icon: ShieldCheck,
    tint: "var(--color-blue-bright)",
    img: "https://images.unsplash.com/photo-1672380135241-c024f7fbfa13?crop=entropy&cs=srgb&fm=jpg&q=85&w=800",
  },
  {
    key: "borderless",
    Icon: Globe2,
    tint: "var(--color-accent)",
    img: "https://images.unsplash.com/photo-1759200345253-4dde70db7c09?crop=entropy&cs=srgb&fm=jpg&q=85&w=800",
  },
  {
    key: "credentials",
    Icon: Award,
    tint: "var(--color-warm)",
    img: "https://images.unsplash.com/photo-1486312338219-ce68d2c6f44d?crop=entropy&cs=srgb&fm=jpg&q=85&w=800",
  },
] as const;

export function LandingPage() {
  const { t } = useTranslation();
  const { currentCountry, localCurrency, payoutRail, countryName } =
    useLocationContext();

  return (
    <div data-testid="landing-page" className="relative overflow-hidden">
      {/* ambient warm glows */}
      <div
        aria-hidden
        className="pointer-events-none absolute -top-32 -left-24 h-96 w-96 rounded-full blur-3xl animate-glow"
        style={{
          background:
            "radial-gradient(circle, color-mix(in srgb, var(--color-coral) 45%, transparent), transparent 70%)",
        }}
      />
      <div
        aria-hidden
        className="pointer-events-none absolute top-40 right-0 h-[28rem] w-[28rem] rounded-full blur-3xl animate-glow"
        style={{
          animationDelay: "1.5s",
          background:
            "radial-gradient(circle, color-mix(in srgb, var(--color-accent) 40%, transparent), transparent 70%)",
        }}
      />

      {/* HERO */}
      <section className="relative max-w-6xl mx-auto px-4 pt-16 pb-20 grid lg:grid-cols-2 gap-12 items-center">
        <div className="text-center lg:text-left">
          <p
            className="animate-fade-up inline-flex items-center gap-2 rounded-full border border-border px-3 py-1 text-xs font-semibold tracking-widest uppercase text-content-secondary"
            style={{ animationDelay: "0.05s" }}
          >
            <span className="h-2 w-2 rounded-full bg-coral animate-glow" />
            {t("landing.tagline")}
          </p>

          <h1
            className="animate-fade-up mt-6 text-4xl sm:text-6xl font-bold tracking-tight leading-[1.05]"
            style={{ animationDelay: "0.15s" }}
          >
            <span className="text-gradient">{t("landing.title")}</span>
          </h1>

          <p
            className="animate-fade-up mt-6 text-content-secondary text-lg max-w-xl mx-auto lg:mx-0 leading-relaxed"
            style={{ animationDelay: "0.28s" }}
          >
            {t("landing.subtitle")}
          </p>

          <div
            className="animate-fade-up mt-8 flex flex-wrap gap-4 justify-center lg:justify-start"
            style={{ animationDelay: "0.4s" }}
          >
            <Link to={`/${currentCountry}/jobs`}>
              <Button data-testid="cta-browse" className="group gap-2 px-6 py-3 text-base">
                {t("landing.ctaBrowse")}
                <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
              </Button>
            </Link>
            <Link to="/auth/register">
              <Button
                data-testid="cta-register"
                variant="secondary"
                className="px-6 py-3 text-base"
              >
                {t("landing.ctaRegister")}
              </Button>
            </Link>
          </div>

          <div
            className="animate-fade-up mt-8 flex flex-wrap items-center gap-6 justify-center lg:justify-start"
            style={{ animationDelay: "0.5s" }}
          >
            {[
              { n: "195+", key: "borderless" },
              { n: "100%", key: "trust" },
              { n: "1-click", key: "credentials" },
            ].map((s) => (
              <div key={s.key} className="text-center lg:text-left">
                <p className="text-2xl font-bold text-content-primary">{s.n}</p>
                <p className="text-xs text-content-muted uppercase tracking-wider">
                  {t(`landing.pillars.${s.key}`)}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* hero image with floating badges */}
        <div
          className="animate-fade-up relative mx-auto w-full max-w-md lg:max-w-none"
          style={{ animationDelay: "0.35s" }}
        >
          <div className="img-zoom warm-glow rounded-lg border border-border overflow-hidden">
            <img
              src={HERO_IMG}
              alt="Verified professionals collaborating across borders"
              className="w-full h-[420px] object-cover"
              loading="eager"
            />
          </div>

          <div className="animate-floaty absolute -left-4 top-10 rounded-md border border-border bg-surface-elevated/90 backdrop-blur px-4 py-3 shadow-xl">
            <div className="flex items-center gap-2">
              <ShieldCheck className="h-5 w-5 text-blue-bright" />
              <div>
                <p className="text-sm font-semibold text-content-primary">
                  {t("profile.verified")}
                </p>
                <p className="text-[11px] text-content-muted">
                  {countryName} · {localCurrency}
                </p>
              </div>
            </div>
          </div>

          <div
            className="animate-floaty absolute -right-3 bottom-8 rounded-md border border-border bg-surface-elevated/90 backdrop-blur px-4 py-3 shadow-xl"
            style={{ animationDelay: "2s" }}
          >
            <div className="flex items-center gap-2">
              <Award className="h-5 w-5 text-warm" />
              <div>
                <p className="text-sm font-semibold text-content-primary">
                  Proof-of-work
                </p>
                <p className="font-mono text-[11px] text-content-muted">
                  {payoutRail}
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* PILLARS */}
      <section className="relative border-t border-border bg-surface-secondary/40">
        <div className="max-w-6xl mx-auto px-4 py-16 grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {PILLARS.map(({ key, Icon, tint, img }, i) => (
            <div
              key={key}
              data-testid={`pillar-${key}`}
              className="animate-fade-up card-lift group rounded-lg border border-border bg-surface-elevated overflow-hidden"
              style={{ animationDelay: `${0.1 * i + 0.1}s` }}
            >
              <div className="img-zoom relative h-32">
                <img
                  src={img}
                  alt={t(`landing.pillars.${key}`)}
                  loading="lazy"
                  className="h-full w-full object-cover"
                />
                <div
                  className="absolute inset-0"
                  style={{
                    background: `linear-gradient(180deg, transparent 30%, color-mix(in srgb, ${tint} 30%, transparent))`,
                  }}
                />
                <span
                  className="absolute bottom-3 left-3 inline-flex h-10 w-10 items-center justify-center rounded-md text-white shadow-lg"
                  style={{ backgroundColor: tint }}
                >
                  <Icon className="h-5 w-5" />
                </span>
              </div>
              <div className="p-5">
                <h2 className="font-semibold mb-2 text-content-primary">
                  {t(`landing.pillars.${key}`)}
                </h2>
                <p className="text-sm text-content-secondary leading-relaxed">
                  {t(`landing.pillarDescriptions.${key}`)}
                </p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* CLOSING CTA */}
      <section className="relative max-w-6xl mx-auto px-4 py-20">
        <div className="hero-gradient warm-glow relative overflow-hidden rounded-lg border border-border px-6 py-14 text-center">
          <div
            aria-hidden
            className="pointer-events-none absolute inset-0 opacity-30 grid-pattern"
          />
          <h2 className="relative text-3xl sm:text-4xl font-bold tracking-tight mb-4">
            <span className="text-gradient">{t("landing.ctaRegister")}</span>
          </h2>
          <p className="relative text-content-secondary max-w-xl mx-auto mb-8">
            {t("landing.subtitle")}
          </p>
          <div className="relative flex flex-wrap gap-4 justify-center">
            <Link to="/auth/register">
              <Button data-testid="cta-register-bottom" className="group gap-2 px-6 py-3 text-base">
                {t("landing.ctaRegister")}
                <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
              </Button>
            </Link>
            <Link to={`/${currentCountry}/jobs`}>
              <Button variant="secondary" className="px-6 py-3 text-base">
                {t("landing.ctaBrowse")}
              </Button>
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
