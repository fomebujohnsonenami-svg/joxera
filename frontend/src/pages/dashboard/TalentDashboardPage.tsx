import { useTranslation } from "react-i18next";
import { LoadingSpinner } from "../../components/ui/LoadingSpinner";
import { useTalentDashboard } from "../../hooks/useProfile";

export function TalentDashboardPage() {
  const { t } = useTranslation();
  const { data, isLoading, isError, refetch } = useTalentDashboard();

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
      <h1 className="text-2xl font-bold mb-8">{t("dashboard.talent.title")}</h1>

      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-10">
        <StatCard
          label={t("dashboard.talent.wallet")}
          value={`${data.currency} ${data.walletBalance.toLocaleString()}`}
          link="/dashboard/wallet"
        />
        <StatCard
          label={t("dashboard.talent.matches")}
          value={String(data.activeMatches)}
        />
        <StatCard
          label={t("dashboard.talent.references")}
          value={String(data.references.length)}
        />
      </div>

      <section>
        <h2 className="text-lg font-semibold mb-4">
          {t("dashboard.talent.credentials")}
        </h2>
        {data.recentCredentials.length === 0 ? (
          <p className="text-slate-500 text-sm">{t("profile.noCredentials")}</p>
        ) : (
          <ul className="space-y-3">
            {data.recentCredentials.map((cred) => (
              <li
                key={cred.id}
                className="rounded-lg border border-slate-800 px-4 py-3 text-sm"
              >
                <span className="font-medium">{cred.jobTitle}</span>
                <span className="text-slate-500 ml-2">· {cred.completedAt}</span>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}

function StatCard({
  label,
  value,
  link,
}: {
  label: string;
  value: string;
  link?: string;
}) {
  const content = (
    <>
      <p className="text-sm text-slate-400">{label}</p>
      <p className="text-2xl font-bold mt-1">{value}</p>
    </>
  );

  if (link) {
    return (
      <a
        href={link}
        className="rounded-xl border border-slate-800 bg-slate-900/50 p-5 block hover:border-joxera-500/40 transition-colors"
      >
        {content}
      </a>
    );
  }

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-5">
      {content}
    </div>
  );
}
