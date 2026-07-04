import { Outlet, Link } from "react-router-dom";
import { useTranslation } from "react-i18next";

export function AuthLayout() {
  const { t } = useTranslation();

  return (
    <div className="min-h-[calc(100vh-3.5rem)] flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <Link to="/" className="font-bold text-2xl">
            <span className="text-joxera-400">Jox</span>
            <span className="text-slate-100">era</span>
          </Link>
        </div>
        <div className="rounded-2xl border border-slate-800 bg-slate-900/50 p-8">
          <Outlet />
        </div>
        <p className="text-center text-xs text-slate-600 mt-4">
          {t("auth.kycNotice")}
        </p>
      </div>
    </div>
  );
}
