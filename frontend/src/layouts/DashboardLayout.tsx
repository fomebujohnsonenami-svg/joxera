import { Outlet, NavLink } from "react-router-dom";
import { useTranslation } from "react-i18next";

export function DashboardLayout() {
  const { t } = useTranslation();

  const tabClass = ({ isActive }: { isActive: boolean }) =>
    `px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
      isActive
        ? "bg-joxera-500/20 text-joxera-400"
        : "text-slate-400 hover:text-slate-200 hover:bg-slate-800"
    }`;

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <div className="flex gap-2 mb-8 border-b border-slate-800 pb-4">
        <NavLink to="/dashboard/wallet" className={tabClass}>
          {t("nav.wallet")}
        </NavLink>
        <NavLink to="/dashboard/talent" className={tabClass}>
          {t("nav.talentDashboard")}
        </NavLink>
        <NavLink to="/dashboard/employer" className={tabClass}>
          {t("nav.employerDashboard")}
        </NavLink>
      </div>
      <Outlet />
    </div>
  );
}
