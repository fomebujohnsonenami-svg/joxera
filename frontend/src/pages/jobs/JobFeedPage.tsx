import { useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import { CountryBadge } from "../../components/ui/CountryBadge";
import { JobCard } from "../../components/jobs/JobCard";
import {
  DEFAULT_JOB_FEED_FILTERS,
  JobFeedFilter,
  type JobFeedFilters,
} from "../../components/jobs/JobFeedFilter";
import { LoadingSpinner } from "../../components/ui/LoadingSpinner";
import { Button } from "../../components/ui/Button";
import { useCountry } from "../../hooks/useCountry";
import { useCombinedJobFeed } from "../../hooks/useJobs";
import { useOnlineStatus } from "../../hooks/useOnlineStatus";

export function JobFeedPage() {
  const { t } = useTranslation();
  const {
    country,
    countryName,
    localCurrency,
    payoutRail,
    isRouteOverride,
    regionalCountry,
  } = useCountry();
  const { isOnline } = useOnlineStatus();

  const [filters, setFilters] = useState<JobFeedFilters>(DEFAULT_JOB_FEED_FILTERS);

  const includeRemote = filters.mode !== "onsite";
  const includeNearby =
    filters.mode !== "remote" &&
    filters.lat != null &&
    filters.lng != null;

  const remoteParams = useMemo(
    () => ({
      country: country!,
      currency: localCurrency,
      field: filters.field || undefined,
      mode: filters.mode === "all" ? "remote" : filters.mode,
      tier: undefined,
    }),
    [country, localCurrency, filters.field, filters.mode]
  );

  const nearbyParams = useMemo(
    () =>
      includeNearby
        ? {
            lat: filters.lat!,
            lng: filters.lng!,
            radiusKm: filters.radiusKm,
            field: filters.field || undefined,
            mode:
              filters.mode === "all" || filters.mode === "hybrid"
                ? undefined
                : filters.mode,
            country: country!,
          }
        : null,
    [includeNearby, filters, country]
  );

  const { jobs, isLoading, isFetching, isError, refetch } = useCombinedJobFeed({
    remote: remoteParams,
    nearby: nearbyParams,
    includeRemote,
    includeNearby,
  });

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 space-y-6">
      <header>
        <div className="flex flex-wrap items-center gap-3 mb-2">
          <h1 className="text-3xl font-bold">
            {t("jobs.feedTitle", { country: countryName })}
          </h1>
          <CountryBadge countryCode={country!} verified size="sm" />
        </div>
        <p className="text-content-secondary mt-2">{t("jobs.feedSubtitle")}</p>
        <p className="font-mono text-xs text-content-muted mt-2">
          {localCurrency} · {payoutRail}
          {includeRemote && includeNearby && " · remote + nearby"}
          {includeRemote && !includeNearby && " · remote only"}
          {!includeRemote && includeNearby && " · nearby only"}
          {isRouteOverride && (
            <span className="ml-2 text-accent">
              (viewing {country}, detected {regionalCountry})
            </span>
          )}
        </p>
        {!isOnline && (
          <p className="text-amber-400 text-sm mt-2">{t("common.offline")}</p>
        )}
        {isFetching && !isLoading && (
          <p className="text-accent/70 text-xs mt-1 animate-pulse">Refreshing…</p>
        )}
      </header>

      <JobFeedFilter value={filters} onChange={setFilters} />

      {isLoading && <LoadingSpinner label={t("jobs.loading")} />}

      {isError && (
        <div className="text-center py-8">
          <p className="text-red-400 mb-4">{t("jobs.error")}</p>
          <Button variant="secondary" onClick={() => refetch()}>
            {t("common.retry")}
          </Button>
        </div>
      )}

      {!isLoading && !isError && jobs.length === 0 && (
        <p className="text-content-muted text-center py-12">{t("jobs.empty")}</p>
      )}

      {!isLoading && jobs.length > 0 && (
        <div className="space-y-4">
          {jobs.map((job) => (
            <JobCard key={job.id} job={job} country={country!} />
          ))}
        </div>
      )}
    </div>
  );
}
