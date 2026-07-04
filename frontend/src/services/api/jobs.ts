import type { Job, JobFeedResponse } from "../../types";
import { fieldToCategory } from "../../constants/jobTaxonomy";
import apiClient from "./client";

export interface ListingDto {
  id: number;
  title: string;
  description: string;
  field: string;
  tier: string;
  mode: string;
  country_code: string;
  currency: string;
  budget: string | number;
  owner_handle: string;
  is_verified_employer: boolean;
  distance_km?: number;
  geo_point?: { type: "Point"; coordinates: [number, number] } | null;
  status: string;
  created_at: string;
}

export interface JobFeedParams {
  country: string;
  currency?: string;
  field?: string;
  mode?: string;
  tier?: string;
  page?: number;
}

export interface NearbyJobsParams {
  lat: number;
  lng: number;
  radiusKm: number;
  field?: string;
  mode?: string;
  tier?: string;
  country?: string;
  page?: number;
}

export interface CreateListingPayload {
  title: string;
  description: string;
  field: string;
  tier: string;
  mode: string;
  country_code: string;
  currency: string;
  budget: number;
  geo_point?: { type: "Point"; coordinates: [number, number] } | null;
  escrow_id?: string;
}

function mapListingToJob(listing: ListingDto): Job {
  const budget =
    typeof listing.budget === "string"
      ? parseFloat(listing.budget)
      : listing.budget;

  return {
    id: String(listing.id),
    title: listing.title,
    description: listing.description,
    country: listing.country_code,
    field: listing.field,
    tier: listing.tier as Job["tier"],
    mode: listing.mode as Job["mode"],
    category: fieldToCategory(listing.field),
    compensation: `${listing.currency} ${budget.toLocaleString()}`,
    compensationAmount: budget,
    compensationCurrency: listing.currency,
    employerHandle: listing.owner_handle,
    isVerifiedEmployer: listing.is_verified_employer,
    distanceKm: listing.distance_km,
    postedAt: listing.created_at,
  };
}

function mapPaginated(data: { results: ListingDto[]; count: number; next: string | null; previous: string | null }): JobFeedResponse {
  return {
    results: data.results.map(mapListingToJob),
    count: data.count,
    next: data.next,
    previous: data.previous,
  };
}

export const jobsApi = {
  async getFeed(params: JobFeedParams): Promise<JobFeedResponse> {
    const { data } = await apiClient.get<{ results: ListingDto[]; count: number; next: string | null; previous: string | null }>(
      `/countries/${params.country}/jobs/`,
      {
        params: {
          field: params.field,
          mode: params.mode,
          tier: params.tier,
          currency: params.currency,
          page: params.page,
        },
      }
    );
    return mapPaginated(data);
  },

  async getNearby(params: NearbyJobsParams): Promise<JobFeedResponse> {
    const { data } = await apiClient.get<{ results: ListingDto[]; count: number; next: string | null; previous: string | null }>(
      "/v3/global/jobs/nearby/",
      {
        params: {
          lat: params.lat,
          lng: params.lng,
          radiusKm: params.radiusKm,
          field: params.field,
          mode: params.mode,
          tier: params.tier,
          country: params.country,
          page: params.page,
        },
      }
    );
    return mapPaginated(data);
  },

  async getById(_country: string, id: string): Promise<Job> {
    const { data } = await apiClient.get<ListingDto>(`/listings/${id}/`);
    return mapListingToJob(data);
  },

  async createListing(payload: CreateListingPayload): Promise<Job> {
    const { data } = await apiClient.post<ListingDto>("/listings/", payload);
    return mapListingToJob(data);
  },
};
