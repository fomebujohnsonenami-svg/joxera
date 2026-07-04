import { FormEvent, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { Button } from "../../components/ui/Button";
import { GoogleLoginButton } from "../../components/auth/GoogleLoginButton";
import { useAuth } from "../../hooks/useAuth";

export function LoginPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const from =
    (location.state as { from?: { pathname: string } })?.from?.pathname ??
    "/dashboard/talent";

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    await login.mutateAsync({ email, password });
    navigate(from, { replace: true });
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-1">{t("auth.loginTitle")}</h1>
      <p className="text-slate-400 text-sm mb-6">{t("auth.loginSubtitle")}</p>

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
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full rounded-lg bg-slate-950 border border-slate-700 px-3 py-2 text-sm focus:outline-none focus:border-joxera-500"
          />
        </div>

        {login.isError && (
          <p className="text-red-400 text-sm">{t("common.error")}</p>
        )}

        <Button type="submit" className="w-full" isLoading={login.isPending}>
          {t("auth.submitLogin")}
        </Button>
      </form>

      <div className="flex items-center gap-3 my-6">
        <div className="h-px flex-1 bg-slate-800" />
        <span className="text-xs text-slate-500">{t("auth.orDivider")}</span>
        <div className="h-px flex-1 bg-slate-800" />
      </div>

      <GoogleLoginButton />

      <p className="text-sm text-slate-500 mt-6 text-center">
        {t("auth.noAccount")}{" "}
        <Link to="/auth/register" className="text-joxera-400 hover:underline">
          {t("nav.register")}
        </Link>
      </p>
    </div>
  );
}
