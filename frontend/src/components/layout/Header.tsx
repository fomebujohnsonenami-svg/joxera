import { Link, NavLink } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useLocationContext } from "../../contexts/LocationProvider";
import { useAuth } from "../../hooks/useAuth";
import { Button } from "../ui/Button";

export function Header() {
  const { t } = useTranslation();
  const { user, isAuthenticated, logout } = useAuth();
  const { currentCountry, localCurrency } = useLocationContext();

  const navLinkClass = ({ isActive }: { isActive: boolean }) =>
    `text-sm transition-colors ${
      isActive ? "text-joxera-400" : "text-slate-400 hover:text-slate-200"
    }`;

  return (
    <header className="border-b border-slate-800 bg-slate-950/80 backdrop-blur sticky top-0 z-50">
      <div className="max-w-6xl mx-auto px-4 h-14 flex items-center justify-between">
        <Link to="/" className="font-bold text-lg tracking-tight">
          <span className="text-joxera-400">Jox</span>
          <span className="text-slate-100">era</span>
        </Link>

        <nav className="hidden sm:flex items-center gap-6">
          <NavLink to="/" className={navLinkClass} end>
            {t("nav.home")}
          </NavLink>
          <NavLink to={`/${currentCountry}/jobs`} className={navLinkClass}>
            {t("nav.jobs")}
          </NavLink>
          {isAuthenticated && (
            <>
              <NavLink to="/dashboard/talent" className={navLinkClass}>
                {t("nav.talentDashboard")}
              </NavLink>
              <NavLink to="/dashboard/employer" className={navLinkClass}>
                {t("nav.employerDashboard")}
              </NavLink>
              {user?.handle && (
                <NavLink to={`/profile/${user.handle}`} className={navLinkClass}>
                  @{user.handle}
                </NavLink>
              )}
            </>
          )}
        </nav>

        <div className="flex items-center gap-2">
          <span className="hidden lg:inline font-mono text-[10px] text-content-muted">
            {currentCountry}/{localCurrency}
          </span>
          {isAuthenticated ? (
            <Button
              variant="ghost"
              onClick={() => logout.mutate()}
              isLoading={logout.isPending}
            >
              {t("nav.logout")}
            </Button>
          ) : (
            <>
              <Link to="/auth/login">
                <Button variant="ghost">{t("nav.login")}</Button>
              </Link>
              <Link to="/auth/register">
                <Button>{t("nav.register")}</Button>
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
