import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import type { Job } from "../types";
import {
  jobsApi,
  type JobFeedParams,
  type NearbyJobsParams,
} from "../services/api/jobs";

export const jobKeys = {
  all: ["jobs"] as const,
  feed: (params: JobFeedParams) => [...jobKeys.all, "feed", params] as const,
  nearby: (params: NearbyJobsParams) => [...jobKeys.all, "nearby", params] as const,
  detail: (country: string, id: string) =>
    [...jobKeys.all, "detail", country, id] as const,
};

const JOB_FEED_STALE_TIME = 60 * 1000;
const JOB_FEED_GC_TIME = 30 * 60 * 1000;

export function useJobFeed(params: JobFeedParams) {
  return useQuery({
    queryKey: jobKeys.feed(params),
    queryFn: () => jobsApi.getFeed(params),
    staleTime: JOB_FEED_STALE_TIME,
    gcTime: JOB_FEED_GC_TIME,
    placeholderData: (previous) => previous,
    enabled: Boolean(params.country),
  });
}

export interface CombinedFeedParams {
  remote: JobFeedParams;
  nearby: NearbyJobsParams | null;
  includeRemote?: boolean;
  includeNearby?: boolean;
}

function mergeJobs(remote: Job[], nearby: Job[]): Job[] {
  const seen = new Set<string>();
  const merged: Job[] = [];

  for (const job of nearby) {
    if (!seen.has(job.id)) {
      seen.add(job.id);
      merged.push(job);
    }
  }
  for (const job of remote) {
    if (!seen.has(job.id)) {
      seen.add(job.id);
      merged.push(job);
    }
  }

  return merged.sort((a, b) => {
    if (a.distanceKm != null && b.distanceKm != null) {
      return a.distanceKm - b.distanceKm;
    }
    if (a.distanceKm != null) return -1;
    if (b.distanceKm != null) return 1;
    return new Date(b.postedAt).getTime() - new Date(a.postedAt).getTime();
  });
}

export function useCombinedJobFeed({
  remote,
  nearby,
  includeRemote = true,
  includeNearby = true,
}: CombinedFeedParams) {
  const remoteQuery = useQuery({
    queryKey: jobKeys.feed(remote),
    queryFn: () => jobsApi.getFeed({ ...remote, mode: remote.mode ?? "remote" }),
    staleTime: JOB_FEED_STALE_TIME,
    gcTime: JOB_FEED_GC_TIME,
    placeholderData: (previous) => previous,
    enabled: includeRemote && Boolean(remote.country),
  });

  const nearbyQuery = useQuery({
    queryKey: nearby ? jobKeys.nearby(nearby) : ["jobs", "nearby", "disabled"],
    queryFn: () => jobsApi.getNearby(nearby!),
    staleTime: JOB_FEED_STALE_TIME,
    gcTime: JOB_FEED_GC_TIME,
    placeholderData: (previous) => previous,
    enabled:
      includeNearby &&
      nearby != null &&
      Number.isFinite(nearby.lat) &&
      Number.isFinite(nearby.lng),
  });

  const jobs = useMemo(() => {
    const remoteJobs = includeRemote ? (remoteQuery.data?.results ?? []) : [];
    const nearbyJobs = includeNearby ? (nearbyQuery.data?.results ?? []) : [];
    return mergeJobs(remoteJobs, nearbyJobs);
  }, [remoteQuery.data, nearbyQuery.data, includeRemote, includeNearby]);

  return {
    jobs,
    remoteQuery,
    nearbyQuery,
    isLoading: remoteQuery.isLoading || nearbyQuery.isLoading,
    isFetching: remoteQuery.isFetching || nearbyQuery.isFetching,
    isError: remoteQuery.isError || nearbyQuery.isError,
    refetch: () => {
      void remoteQuery.refetch();
      void nearbyQuery.refetch();
    },
  };
}

export function useJobDetail(country: string, id: string, currency?: string) {
  return useQuery({
    queryKey: [...jobKeys.detail(country, id), currency ?? "default"],
    queryFn: () => jobsApi.getById(country, id),
    staleTime: JOB_FEED_STALE_TIME,
    gcTime: JOB_FEED_GC_TIME,
    enabled: Boolean(country && id),
  });
}
