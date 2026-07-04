import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import {
  ShieldCheck,
  Globe2,
  Award,
  Sparkles,
  ArrowRight,
  Zap,
  Users,
  CheckCircle2,
  Rocket,
  Layers,
} from "lucide-react";
import { useLocationContext } from "../contexts/LocationProvider";
import { useAuth } from "../hooks/useAuth";
import { GoogleLoginButton } from "../components/auth/GoogleLoginButton";

const HERO_IMG =
  "https://images.pexels.com/photos/5439474/pexels-photo-5439474.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940";

const PILLARS = [
  {
    key: "inclusive",
    Icon: Sparkles,
    tint: "var(--v-magenta)",
    accent: "linear-gradient(135deg, var(--v-magenta), var(--v-tangerine))",
    img: "https://images.pexels.com/photos/7491017/pexels-photo-7491017.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
  },
  {
    key: "trust",
    Icon: ShieldCheck,
    tint: "var(--v-cyan)",
    accent: "linear-gradient(135deg, var(--v-cyan), var(--v-indigo))",
    img: "https://images.unsplash.com/photo-1672380135241-c024f7fbfa13?crop=entropy&cs=srgb&fm=jpg&q=85&w=800",
  },
  {
    key: "borderless",
    Icon: Globe2,
    tint: "var(--v-emerald)",
    accent: "linear-gradient(135deg, var(--v-lime), var(--v-teal))",
    img: "https://images.unsplash.com/photo-1759200345253-4dde70db7c09?crop=entropy&cs=srgb&fm=jpg&q=85&w=800",
  },
  {
    key: "credentials",
    Icon: Award,
    tint: "var(--v-tangerine)",
    accent: "linear-gradient(135deg, var(--v-tangerine), var(--v-magenta))",
    img: "https://images.unsplash.com/photo-1486312338219-ce68d2c6f44d?crop=entropy&cs=srgb&fm=jpg&q=85&w=800",
  },
] as const;

const COUNTRIES = [
  "🇺🇸 United States",
  "🇳🇬 Nigeria",
  "🇧🇷 Brazil",
  "🇮🇳 India",
  "🇰🇪 Kenya",
  "🇩🇪 Germany",
  "🇲🇽 Mexico",
  "🇵🇭 Philippines",
  "🇬🇧 United Kingdom",
  "🇮🇩 Indonesia",
  "🇿🇦 South Africa",
  "🇪🇬 Egypt",
  "🇻🇳 Vietnam",
  "🇦🇷 Argentina",
  "🇹🇷 Türkiye",
  "🇵🇱 Poland",
  "🇨🇦 Canada",
  "🇨🇴 Colombia",
];

const HOW_STEPS = [
  {
    Icon: ShieldCheck,
    title: "Verify once",
    desc: "Complete a one-time KYC pass — every profile you meet is real.",
    color: "var(--v-cyan)",
  },
  {
    Icon: Rocket,
    title: "Match instantly",
    desc: "Skill-embedding search across 195+ countries, no borders, no friction.",
    color: "var(--v-magenta)",
  },
  {
    Icon: Layers,
    title: "Get paid on rails",
    desc: "Escrow with local payout rails: ACH, PIX, UPI, SEPA — you pick.",
    color: "var(--v-lime)",
  },
  {
    Icon: Award,
    title: "Mint your proof",
    desc: "Every completed gig becomes an Ed25519-signed credential you own.",
    color: "var(--v-tangerine)",
  },
];

export function LandingPage() {
  const { t } = useTranslation();
  const { currentCountry, localCurrency, payoutRail, countryName } =
    useLocationContext();
  const { isAuthenticated } = useAuth();

  return (
    <div
      data-testid="landing-page"
      className="landing-surface relative overflow-hidden"
    >
      {/* aurora blobs */}
      <div
        aria-hidden
        className="aurora-blob animate-aurora"
        style={{
          top: "-8rem",
          left: "-6rem",
          width: "28rem",
          height: "28rem",
          background:
            "radial-gradient(circle at 30% 30%, var(--v-magenta), transparent 60%)",
        }}
      />
      <div
        aria-hidden
        className="aurora-blob animate-aurora"
        style={{
          top: "6rem",
          right: "-8rem",
          width: "32rem",
          height: "32rem",
          animationDelay: "3s",
          background:
            "radial-gradient(circle at 50% 40%, var(--v-cyan), transparent 65%)",
        }}
      />
      <div
        aria-hidden
        className="aurora-blob animate-aurora"
        style={{
          top: "38rem",
          left: "20%",
          width: "36rem",
          height: "36rem",
          animationDelay: "6s",
          background:
            "radial-gradient(circle at 40% 50%, var(--v-lime), transparent 60%)",
        }}
      />
      <div aria-hidden className="noise-overlay" />

      <div className="landing-content">
        {/* HERO */}
        <section className="relative max-w-6xl mx-auto px-4 pt-16 pb-14 grid lg:grid-cols-[1.1fr_0.9fr] gap-12 items-center">
          <div className="text-center lg:text-left">
            <p
              className="animate-fade-up delay-100 inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/5 backdrop-blur px-3 py-1 text-xs font-semibold tracking-widest uppercase"
              style={{ color: "var(--v-lime)" }}
            >
              <span
                className="h-2 w-2 rounded-full animate-glow"
                style={{ background: "var(--v-lime)" }}
              />
              {t("landing.tagline")}
              <Zap className="h-3 w-3" />
            </p>

            <h1
              className="animate-fade-up delay-200 mt-6 text-5xl sm:text-7xl font-bold tracking-tight leading-[0.98]"
              data-testid="landing-heading"
            >
              <span className="text-gradient-vibrant">End global</span>
              <br />
              <span className="font-serif-accent text-white">
                un
              </span>
              <span className="text-gradient-sunset">employment</span>
              <span
                aria-hidden
                className="inline-block ml-2 animate-sparkle"
                style={{ color: "var(--v-lime)" }}
              >
                ✦
              </span>
            </h1>

            <p className="animate-fade-up delay-300 mt-6 text-white/70 text-lg max-w-xl mx-auto lg:mx-0 leading-relaxed">
              {t("landing.subtitle")}
            </p>

            <div className="animate-fade-up delay-400 mt-8 flex flex-wrap gap-3 justify-center lg:justify-start">
              <Link to={`/${currentCountry}/jobs`}>
                <button data-testid="cta-browse" className="btn-vibrant group">
                  {t("landing.ctaBrowse")}
                  <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
                </button>
              </Link>
              {!isAuthenticated && (
                <div data-testid="landing-google-login">
                  <GoogleLoginButton variant="pill" />
                </div>
              )}
              <Link to="/auth/register">
                <button data-testid="cta-register" className="btn-ghost-glow">
                  {t("landing.ctaRegister")}
                </button>
              </Link>
            </div>

            {/* stats row */}
            <div className="animate-fade-up delay-500 mt-10 flex flex-wrap items-center gap-8 justify-center lg:justify-start">
              {[
                { n: "195+", key: "borderless", color: "var(--v-lime)" },
                { n: "100%", key: "trust", color: "var(--v-cyan)" },
                { n: "1-click", key: "credentials", color: "var(--v-magenta)" },
              ].map((s, i) => (
                <div
                  key={s.key}
                  className="animate-count-up text-center lg:text-left"
                  style={{ animationDelay: `${0.6 + i * 0.15}s` }}
                >
                  <p
                    className="text-3xl sm:text-4xl font-bold tracking-tight"
                    style={{
                      background: `linear-gradient(120deg, ${s.color}, white)`,
                      WebkitBackgroundClip: "text",
                      backgroundClip: "text",
                      color: "transparent",
                    }}
                  >
                    {s.n}
                  </p>
                  <p className="text-[11px] text-white/50 uppercase tracking-widest mt-1">
                    {t(`landing.pillars.${s.key}`)}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* hero image with floating badges */}
          <div
            className="animate-tilt-in delay-300 relative mx-auto w-full max-w-md lg:max-w-none"
            data-testid="landing-hero-image"
          >
            <div className="conic-border vibrant-glow">
              <div className="img-zoom rounded-[23px] overflow-hidden">
                <img
                  src={HERO_IMG}
                  alt="Verified professionals collaborating across borders"
                  className="w-full h-[440px] object-cover"
                  loading="eager"
                />
                <div
                  aria-hidden
                  className="absolute inset-0 pointer-events-none"
                  style={{
                    background:
                      "linear-gradient(180deg, transparent 50%, rgba(11,7,32,0.55))",
                  }}
                />
              </div>
            </div>

            <div
              className="animate-floaty absolute -left-4 top-8 rounded-2xl border border-white/20 bg-white/10 backdrop-blur-lg px-4 py-3 shadow-2xl"
              style={{
                boxShadow:
                  "0 20px 40px -10px color-mix(in srgb, var(--v-cyan) 40%, transparent)",
              }}
            >
              <div className="flex items-center gap-2">
                <ShieldCheck
                  className="h-5 w-5"
                  style={{ color: "var(--v-cyan)" }}
                />
                <div>
                  <p className="text-sm font-semibold text-white">
                    {t("profile.verified")}
                  </p>
                  <p className="text-[11px] text-white/60">
                    {countryName} · {localCurrency}
                  </p>
                </div>
              </div>
            </div>

            <div
              className="animate-floaty absolute -right-3 bottom-12 rounded-2xl border border-white/20 bg-white/10 backdrop-blur-lg px-4 py-3 shadow-2xl"
              style={{
                animationDelay: "2s",
                boxShadow:
                  "0 20px 40px -10px color-mix(in srgb, var(--v-magenta) 40%, transparent)",
              }}
            >
              <div className="flex items-center gap-2">
                <Award
                  className="h-5 w-5"
                  style={{ color: "var(--v-tangerine)" }}
                />
                <div>
                  <p className="text-sm font-semibold text-white">
                    Proof-of-work
                  </p>
                  <p className="font-mono text-[11px] text-white/60">
                    {payoutRail}
                  </p>
                </div>
              </div>
            </div>

            <div
              className="animate-floaty absolute left-8 -bottom-4 rounded-2xl border border-white/20 bg-white/10 backdrop-blur-lg px-4 py-3 shadow-2xl"
              style={{
                animationDelay: "1s",
                boxShadow:
                  "0 20px 40px -10px color-mix(in srgb, var(--v-lime) 40%, transparent)",
              }}
            >
              <div className="flex items-center gap-2">
                <Users
                  className="h-5 w-5"
                  style={{ color: "var(--v-lime)" }}
                />
                <div>
                  <p className="text-sm font-semibold text-white">
                    12,483 hired
                  </p>
                  <p className="text-[11px] text-white/60">this month</p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* MARQUEE — country ticker */}
        <section
          aria-label="Countries served"
          data-testid="country-marquee"
          className="relative border-y border-white/10 py-5 overflow-hidden"
          style={{
            background:
              "linear-gradient(90deg, rgba(255,255,255,0.02), rgba(255,255,255,0.05), rgba(255,255,255,0.02))",
          }}
        >
          <div
            aria-hidden
            className="pointer-events-none absolute inset-y-0 left-0 w-24 z-10"
            style={{
              background:
                "linear-gradient(90deg, var(--v-ink), transparent)",
            }}
          />
          <div
            aria-hidden
            className="pointer-events-none absolute inset-y-0 right-0 w-24 z-10"
            style={{
              background:
                "linear-gradient(270deg, var(--v-ink), transparent)",
            }}
          />
          <div className="flex gap-3 animate-marquee whitespace-nowrap w-max">
            {[...COUNTRIES, ...COUNTRIES].map((c, i) => (
              <span key={`${c}-${i}`} className="ticker-chip">
                {c}
              </span>
            ))}
          </div>
        </section>

        {/* PILLARS */}
        <section className="relative">
          <div className="max-w-6xl mx-auto px-4 py-20">
            <div className="mb-10 max-w-2xl">
              <p
                className="text-xs font-semibold uppercase tracking-[0.25em]"
                style={{ color: "var(--v-cyan)" }}
              >
                Why Joxera
              </p>
              <h2 className="mt-3 text-4xl sm:text-5xl font-bold tracking-tight">
                <span className="text-white">Built for </span>
                <span className="font-serif-accent text-gradient-sunset">
                  everyone
                </span>
                <span className="text-white">, everywhere.</span>
              </h2>
            </div>

            <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
              {PILLARS.map(({ key, Icon, tint, accent, img }, i) => (
                <div
                  key={key}
                  data-testid={`pillar-${key}`}
                  className="animate-fade-up card-tilt group rounded-2xl border border-white/10 bg-white/[0.03] overflow-hidden backdrop-blur"
                  style={{ animationDelay: `${0.1 * i + 0.1}s` }}
                >
                  <div className="img-zoom relative h-36">
                    <img
                      src={img}
                      alt={t(`landing.pillars.${key}`)}
                      loading="lazy"
                      className="h-full w-full object-cover"
                    />
                    <div
                      className="absolute inset-0"
                      style={{
                        background: `linear-gradient(180deg, transparent 20%, color-mix(in srgb, ${tint} 55%, transparent) 100%)`,
                      }}
                    />
                    <span
                      className="absolute bottom-3 left-3 inline-flex h-11 w-11 items-center justify-center rounded-xl text-white shadow-lg"
                      style={{ background: accent }}
                    >
                      <Icon className="h-5 w-5" />
                    </span>
                  </div>
                  <div className="p-5">
                    <h3 className="font-semibold mb-2 text-white">
                      {t(`landing.pillars.${key}`)}
                    </h3>
                    <p className="text-sm text-white/60 leading-relaxed">
                      {t(`landing.pillarDescriptions.${key}`)}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* HOW IT WORKS */}
        <section className="relative">
          <div className="max-w-6xl mx-auto px-4 pb-24">
            <div className="mb-12 flex flex-wrap items-end justify-between gap-4">
              <div className="max-w-xl">
                <p
                  className="text-xs font-semibold uppercase tracking-[0.25em]"
                  style={{ color: "var(--v-magenta)" }}
                >
                  How it works
                </p>
                <h2 className="mt-3 text-4xl sm:text-5xl font-bold tracking-tight text-white">
                  Four steps from{" "}
                  <span className="font-serif-accent text-gradient-vibrant">
                    hello
                  </span>{" "}
                  to hired.
                </h2>
              </div>
            </div>

            <div className="relative grid md:grid-cols-2 lg:grid-cols-4 gap-6">
              {/* connecting line */}
              <div
                aria-hidden
                className="hidden lg:block absolute top-10 left-[12%] right-[12%] h-px"
                style={{
                  background:
                    "linear-gradient(90deg, transparent, var(--v-cyan), var(--v-magenta), var(--v-lime), var(--v-tangerine), transparent)",
                  opacity: 0.5,
                }}
              />
              {HOW_STEPS.map(({ Icon, title, desc, color }, i) => (
                <div
                  key={title}
                  data-testid={`how-step-${i}`}
                  className="animate-fade-up relative rounded-2xl border border-white/10 bg-white/[0.04] p-6 backdrop-blur card-lift"
                  style={{ animationDelay: `${0.15 * i}s` }}
                >
                  <div className="flex items-center justify-between mb-4">
                    <span
                      className="inline-flex h-11 w-11 items-center justify-center rounded-xl shadow-lg"
                      style={{
                        background: `linear-gradient(135deg, ${color}, color-mix(in srgb, ${color} 30%, black))`,
                      }}
                    >
                      <Icon className="h-5 w-5 text-white" />
                    </span>
                    <span
                      className="font-mono text-xs px-2 py-1 rounded-full border border-white/10"
                      style={{ color, background: "rgba(255,255,255,0.03)" }}
                    >
                      0{i + 1}
                    </span>
                  </div>
                  <h3 className="text-lg font-semibold text-white mb-1">
                    {title}
                  </h3>
                  <p className="text-sm text-white/60 leading-relaxed">
                    {desc}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* SIGN-IN CTA (with Google) — hidden if authed */}
        {!isAuthenticated && (
          <section className="relative">
            <div className="max-w-3xl mx-auto px-4 pb-24">
              <div
                className="conic-border"
                data-testid="landing-signin-card"
              >
                <div className="px-6 py-12 sm:px-12 sm:py-14 text-center">
                  <p
                    className="text-xs font-semibold uppercase tracking-[0.25em] mb-3"
                    style={{ color: "var(--v-lime)" }}
                  >
                    Free to join
                  </p>
                  <h2 className="text-3xl sm:text-5xl font-bold tracking-tight text-white leading-[1.05]">
                    Sign in in{" "}
                    <span className="font-serif-accent text-gradient-vibrant">
                      one tap.
                    </span>
                  </h2>
                  <p className="mt-4 text-white/60 max-w-lg mx-auto">
                    Continue with Google — we&apos;ll verify your identity and
                    onboard you to your regional dashboard automatically.
                  </p>

                  <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-3">
                    <div data-testid="landing-google-login-primary">
                      <GoogleLoginButton variant="pill" />
                    </div>
                    <span className="text-white/40 text-sm">or</span>
                    <Link to="/auth/register">
                      <button
                        data-testid="cta-register-inline"
                        className="btn-ghost-glow"
                      >
                        Use email instead
                      </button>
                    </Link>
                  </div>

                  <ul className="mt-8 flex flex-wrap items-center justify-center gap-x-6 gap-y-2 text-xs text-white/50">
                    <li className="inline-flex items-center gap-1.5">
                      <CheckCircle2
                        className="h-3.5 w-3.5"
                        style={{ color: "var(--v-lime)" }}
                      />
                      Verified identity
                    </li>
                    <li className="inline-flex items-center gap-1.5">
                      <CheckCircle2
                        className="h-3.5 w-3.5"
                        style={{ color: "var(--v-cyan)" }}
                      />
                      Local payouts
                    </li>
                    <li className="inline-flex items-center gap-1.5">
                      <CheckCircle2
                        className="h-3.5 w-3.5"
                        style={{ color: "var(--v-magenta)" }}
                      />
                      Signed credentials
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          </section>
        )}

        {/* CLOSING CTA */}
        <section className="relative">
          <div className="max-w-6xl mx-auto px-4 pb-24">
            <div
              className="relative overflow-hidden rounded-3xl border border-white/10 px-6 py-16 text-center"
              style={{
                background:
                  "radial-gradient(ellipse at 20% 20%, color-mix(in srgb, var(--v-magenta) 30%, transparent), transparent 55%), radial-gradient(ellipse at 80% 80%, color-mix(in srgb, var(--v-cyan) 30%, transparent), transparent 55%), linear-gradient(135deg, var(--v-ink-2), var(--v-ink))",
              }}
            >
              <div
                aria-hidden
                className="pointer-events-none absolute inset-0 opacity-25 grid-pattern"
              />
              <div
                aria-hidden
                className="pointer-events-none absolute -top-24 -right-16 h-72 w-72 rounded-full blur-3xl animate-glow"
                style={{
                  background:
                    "radial-gradient(circle, var(--v-tangerine), transparent 65%)",
                }}
              />
              <h2 className="relative text-4xl sm:text-6xl font-bold tracking-tight mb-4 leading-[1.05]">
                <span className="text-white">Ready to </span>
                <span className="text-gradient-vibrant">go borderless?</span>
              </h2>
              <p className="relative text-white/70 max-w-xl mx-auto mb-8">
                {t("landing.subtitle")}
              </p>
              <div className="relative flex flex-wrap gap-3 justify-center">
                <Link to="/auth/register">
                  <button
                    data-testid="cta-register-bottom"
                    className="btn-vibrant group"
                  >
                    {t("landing.ctaRegister")}
                    <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
                  </button>
                </Link>
                <Link to={`/${currentCountry}/jobs`}>
                  <button
                    data-testid="cta-browse-bottom"
                    className="btn-ghost-glow"
                  >
                    {t("landing.ctaBrowse")}
                  </button>
                </Link>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
