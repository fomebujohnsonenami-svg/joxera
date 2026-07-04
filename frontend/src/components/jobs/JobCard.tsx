import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useCountry } from "../../hooks/useCountry";
import type { Job } from "../../types";
import { formatRegionalPrice } from "../../utils/currency";
import { Badge } from "../ui/Badge";
import { Button } from "../ui/Button";

interface JobCardProps {
  job: Job;
  country: string;
}

export function JobCard({ job, country }: JobCardProps) {
  const { t, i18n } = useTranslation();
  const { localCurrency, payoutRail } = useCountry();

  const displayPrice = formatRegionalPrice(job, localCurrency, i18n.language);

  return (
    <article className="rounded-xl border border-border bg-surface-elevated/50 p-5 hover:border-blue-bright/30 transition-colors">
        <div className="flex items-start justify-between gap-3">
        <div>
          <h3 className="font-semibold text-lg text-content-primary">{job.title}</h3>
          <p className="text-sm text-content-secondary mt-1 line-clamp-2">
            {job.description}
          </p>
        </div>
        <div className="flex flex-col items-end gap-1">
          <Badge>{t(`jobs.category.${job.category}`)}</Badge>
          {job.distanceKm != null && (
            <span className="font-mono text-[10px] text-accent">
              {job.distanceKm.toFixed(1)} km
            </span>
          )}
        </div>
      </div>
      <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
        <div className="text-sm text-content-muted">
          <span className="font-mono font-medium text-content-primary">
            {displayPrice}
          </span>
          <span className="mx-2">·</span>
          <span className="font-mono text-xs text-accent">{payoutRail}</span>
          <span className="mx-2">·</span>
          <span>@{job.employerHandle}</span>
          {job.isVerifiedEmployer && (
            <Badge variant="success">
              <span className="ml-2">{t("jobs.detail.verifiedEmployer")}</span>
            </Badge>
          )}
        </div>
        <Link to={`/${country}/jobs/${job.id}`}>
          <Button variant="secondary">{t("jobs.viewDetails")}</Button>
        </Link>
      </div>
    </article>
  );
}
