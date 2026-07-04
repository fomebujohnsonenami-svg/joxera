import { Link, useParams } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { Badge } from "../../components/ui/Badge";
import { Button } from "../../components/ui/Button";
import { LoadingSpinner } from "../../components/ui/LoadingSpinner";
import { useCountry } from "../../hooks/useCountry";
import { useJobDetail } from "../../hooks/useJobs";
import { formatRegionalPrice } from "../../utils/currency";

export function JobDetailPage() {
  const { t, i18n } = useTranslation();
  const { id } = useParams<{ id: string }>();
  const { country, localCurrency, payoutRail } = useCountry();

  const { data: job, isLoading, isError, refetch } = useJobDetail(
    country!,
    id!,
    localCurrency
  );

  if (isLoading) {
    return <LoadingSpinner label={t("common.loading")} />;
  }

  if (isError || !job) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-16 text-center">
        <p className="text-red-400 mb-4">{t("common.error")}</p>
        <Button variant="secondary" onClick={() => refetch()}>
          {t("common.retry")}
        </Button>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto px-4 py-8">
      <Link
        to={`/${country}/jobs`}
        className="text-sm text-joxera-400 hover:underline mb-6 inline-block"
      >
        ← {t("jobs.detail.back")}
      </Link>

      <article className="rounded-2xl border border-slate-800 bg-slate-900/50 p-8">
        <div className="flex items-start justify-between gap-4 mb-4">
          <h1 className="text-3xl font-bold">{job.title}</h1>
          <Badge>{t(`jobs.category.${job.category}`)}</Badge>
        </div>

        <p className="text-slate-300 leading-relaxed mb-6">{job.description}</p>

        <div className="border-t border-slate-800 pt-6 space-y-3 text-sm">
          <p>
            <span className="text-slate-500">{t("jobs.detail.postedBy")}: </span>
            <Link
              to={`/profile/${job.employerHandle}`}
              className="text-joxera-400 hover:underline"
            >
              @{job.employerHandle}
            </Link>
            {job.isVerifiedEmployer && (
              <Badge variant="success">
                <span className="ml-2">{t("jobs.detail.verifiedEmployer")}</span>
              </Badge>
            )}
          </p>
          <p className="text-content-secondary">
            <span className="font-mono font-medium text-content-primary">
              {formatRegionalPrice(job, localCurrency, i18n.language)}
            </span>
            <span className="mx-2 text-content-muted">·</span>
            <span className="font-mono text-xs text-accent">{payoutRail}</span>
          </p>
        </div>

        <Button className="mt-8 w-full sm:w-auto">{t("jobs.detail.apply")}</Button>
      </article>
    </div>
  );
}
