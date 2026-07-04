import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { Button } from "../../components/ui/Button";
import { GoogleLoginButton } from "../../components/auth/GoogleLoginButton";
import { useAuth } from "../../hooks/useAuth";
import { ISO_COUNTRIES } from "../../utils/countries";

export function RegisterPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { register, startKyc } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [handle, setHandle] = useState("");
  const [country, setCountry] = useState("US");
  const [role, setRole] = useState<"talent" | "employer">("talent");

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    await register.mutateAsync({ email, password, handle, country, role });

    try {
      const { redirectUrl } = await startKyc.mutateAsync();
      if (redirectUrl) {
        window.location.href = redirectUrl;
        return;
      }
    } catch {
      // KYC endpoint may not exist yet — proceed to dashboard
    }

    navigate(role === "employer" ? "/dashboard/employer" : "/dashboard/talent");
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-1">{t("auth.registerTitle")}</h1>
      <p className="text-slate-400 text-sm mb-6">{t("auth.registerSubtitle")}</p>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="email" className="block text-sm text-slate-400 mb-1">
            {t("auth.email")}
          </label>
          <input
            id="email"
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full rounded-lg bg-slate-950 border border-slate-700 px-3 py-2 text-sm focus:outline-none focus:border-joxera-500"
          />
        </div>
        <div>
          <label
            htmlFor="password"
            className="block text-sm text-slate-400 mb-1"
          >
            {t("auth.password")}
          </label>
          <input
            id="password"
            type="password"
            required
            minLength={8}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full rounded-lg bg-slate-950 border border-slate-700 px-3 py-2 text-sm focus:outline-none focus:border-joxera-500"
          />
        </div>
        <div>
          <label htmlFor="handle" className="block text-sm text-slate-400 mb-1">
            {t("auth.handle")}
          </label>
          <input
            id="handle"
            type="text"
            required
            pattern="[a-zA-Z0-9_]{3,30}"
            value={handle}
            onChange={(e) => setHandle(e.target.value)}
            className="w-full rounded-lg bg-slate-950 border border-slate-700 px-3 py-2 text-sm focus:outline-none focus:border-joxera-500"
          />
        </div>
        <div>
          <label htmlFor="country" className="block text-sm text-slate-400 mb-1">
            {t("auth.country")}
          </label>
          <select
            id="country"
            value={country}
            onChange={(e) => setCountry(e.target.value)}
            className="w-full rounded-lg bg-slate-950 border border-slate-700 px-3 py-2 text-sm focus:outline-none focus:border-joxera-500"
          >
            {Object.entries(ISO_COUNTRIES).map(([code, name]) => (
              <option key={code} value={code}>
                {code} — {name}
              </option>
            ))}
          </select>
        </div>
        <fieldset>
          <legend className="block text-sm text-slate-400 mb-2">
            {t("auth.role")}
          </legend>
          <div className="flex gap-4">
            <label className="flex items-center gap-2 text-sm">
              <input
                type="radio"
                name="role"
                value="talent"
                checked={role === "talent"}
                onChange={() => setRole("talent")}
              />
              {t("auth.roleTalent")}
            </label>
            <label className="flex items-center gap-2 text-sm">
              <input
                type="radio"
                name="role"
                value="employer"
                checked={role === "employer"}
                onChange={() => setRole("employer")}
              />
              {t("auth.roleEmployer")}
            </label>
          </div>
        </fieldset>

        {register.isError && (
          <p className="text-red-400 text-sm">{t("common.error")}</p>
        )}

        <Button
          type="submit"
          className="w-full"
          isLoading={register.isPending || startKyc.isPending}
        >
          {t("auth.submitRegister")}
        </Button>
      </form>

      <div className="flex items-center gap-3 my-6">
        <div className="h-px flex-1 bg-slate-800" />
        <span className="text-xs text-slate-500">{t("auth.orDivider")}</span>
        <div className="h-px flex-1 bg-slate-800" />
      </div>

      <GoogleLoginButton />

      <p className="text-sm text-slate-500 mt-6 text-center">
        {t("auth.hasAccount")}{" "}
        <Link to="/auth/login" className="text-joxera-400 hover:underline">
          {t("nav.login")}
        </Link>
      </p>
    </div>
  );
}
