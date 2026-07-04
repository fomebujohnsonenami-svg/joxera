import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { Button } from "../../components/ui/Button";
import { LoadingSpinner } from "../../components/ui/LoadingSpinner";
import { useEmployerDashboard } from "../../hooks/useProfile";

export function EmployerDashboardPage() {
  const { t } = useTranslation();
  const { data, isLoading, isError, refetch } = useEmployerDashboard();

  if (isLoading) return <LoadingSpinner label={t("common.loading")} />;

  if (isError || !data) {
    return (
      <div className="text-center py-12">
        <p className="text-red-400 mb-4">{t("common.error")}</p>
        <button
          onClick={() => refetch()}
          className="text-joxera-400 hover:underline text-sm"
        >
          {t("common.retry")}
        </button>
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-2xl font-bold">{t("dashboard.employer.title")}</h1>
        <Link to="/dashboard/employer/post">
          <Button>{t("dashboard.employer.postJob")}</Button>
        </Link>
      </div>

      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          label={t("dashboard.employer.escrow")}
          value={`${data.currency} ${data.escrowBalance.toLocaleString()}`}
        />
        <StatCard
          label={t("dashboard.employer.activeJobs")}
          value={String(data.activeJobs)}
        />
        <StatCard
          label={t("dashboard.employer.hires")}
          value={String(data.recentHires)}
        />
        <StatCard
          label={t("dashboard.employer.pending")}
          value={String(data.pendingApplications)}
        />
      </div>
    </div>
  );
}

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-5">
      <p className="text-sm text-slate-400">{label}</p>
      <p className="text-2xl font-bold mt-1">{value}</p>
    </div>
  );
}
