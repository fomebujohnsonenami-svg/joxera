"""
Cosine-similarity job matching with geo-distance weighting for on-site roles.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from django.conf import settings
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.db import connection
from pgvector.django import CosineDistance

from jobs.models import Listing, ListingMode, ListingStatus


@dataclass
class MatchResult:
    listing: Listing
    similarity: float
    geo_factor: float
    match_score: float
    distance_km: float | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "listing_id": self.listing.id,
            "title": self.listing.title,
            "field": self.listing.field,
            "mode": self.listing.mode,
            "tier": self.listing.tier,
            "country_code": self.listing.country_code,
            "budget": str(self.listing.budget),
            "currency": self.listing.currency,
            "skill_tags": self.listing.skill_tags,
            "similarity": round(self.similarity, 4),
            "geo_factor": round(self.geo_factor, 4),
            "match_score": round(self.match_score, 4),
            "distance_km": round(self.distance_km, 2) if self.distance_km is not None else None,
        }


def _geo_factor(distance_km: float | None, mode: str) -> float:
    if mode not in (ListingMode.ONSITE, ListingMode.HYBRID):
        return 1.0
    if distance_km is None:
        return 0.85
    decay = getattr(settings, "MATCH_GEO_DECAY_KM", 50.0)
    return 1.0 / (1.0 + distance_km / decay)


def match_listings_for_talent(
    talent_embedding: list[float],
    *,
    lat: float | None = None,
    lng: float | None = None,
    limit: int = 20,
    country_code: str | None = None,
    max_geo_km: float = 200.0,
) -> list[MatchResult]:
    qs = Listing.objects.filter(
        status=ListingStatus.PUBLISHED,
        skill_embedding__isnull=False,
    ).select_related("owner")

    if country_code:
        qs = qs.filter(country_code=country_code.upper())

    origin: Point | None = None
    if lat is not None and lng is not None:
        origin = Point(lng, lat, srid=4326)
        qs = qs.annotate(_geo_dist=Distance("geo_point", origin))

    qs = qs.annotate(_cosine_dist=CosineDistance("skill_embedding", talent_embedding))
    candidates = list(qs.order_by("_cosine_dist")[: max(limit * 3, 30)])

    results: list[MatchResult] = []
    for listing in candidates:
        cosine_dist = float(getattr(listing, "_cosine_dist", 1.0))
        similarity = max(0.0, 1.0 - cosine_dist)

        distance_km: float | None = None
        if (
            origin
            and listing.geo_point
            and listing.mode in (ListingMode.ONSITE, ListingMode.HYBRID)
        ):
            geo_dist = getattr(listing, "_geo_dist", None)
            if geo_dist is not None:
                distance_km = geo_dist.km
            else:
                distance_km = listing.geo_point.distance(origin) * 111.32
            if distance_km > max_geo_km:
                continue

        geo_f = _geo_factor(distance_km, listing.mode)
        match_score = similarity * geo_f

        results.append(
            MatchResult(
                listing=listing,
                similarity=similarity,
                geo_factor=geo_f,
                match_score=match_score,
                distance_km=distance_km,
            )
        )

    results.sort(key=lambda r: r.match_score, reverse=True)
    return results[:limit]


def match_listings_raw_sql(
    talent_embedding: list[float],
    *,
    lat: float | None = None,
    lng: float | None = None,
    limit: int = 20,
    country_code: str | None = None,
) -> list[dict[str, Any]]:
    """
    pgvector cosine search with geo-weighting via raw SQL (<=> operator).
    """
    decay = getattr(settings, "MATCH_GEO_DECAY_KM", 50.0)
    vector_literal = "[" + ",".join(str(v) for v in talent_embedding) + "]"

    has_geo = lat is not None and lng is not None
    params: list[Any] = [vector_literal, decay]
    geo_origin = "ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography" if has_geo else "NULL::geography"

    if has_geo:
        params.extend([lng, lat, lng, lat])

    params.extend([vector_literal, decay])
    if has_geo:
        params.extend([lng, lat, lng, lat])

    country_clause = ""
    if country_code:
        country_clause = "AND l.country_code = %s"
        params.append(country_code.upper())

    params.append(limit)

    sql = f"""
        SELECT
            l.id AS listing_id,
            l.title,
            l.field,
            l.mode,
            l.tier,
            l.country_code,
            l.budget,
            l.currency,
            l.skill_tags,
            1 - (l.skill_embedding <=> %s::vector) AS similarity,
            CASE
                WHEN l.mode IN ('onsite', 'hybrid')
                     AND l.geo_point IS NOT NULL
                     AND {geo_origin} IS NOT NULL
                THEN 1.0 / (
                    1.0 + ST_Distance(l.geo_point::geography, {geo_origin}) / 1000.0 / %s
                )
                ELSE 1.0
            END AS geo_factor,
            (
                (1 - (l.skill_embedding <=> %s::vector))
                * CASE
                    WHEN l.mode IN ('onsite', 'hybrid')
                         AND l.geo_point IS NOT NULL
                         AND {geo_origin} IS NOT NULL
                    THEN 1.0 / (
                        1.0 + ST_Distance(l.geo_point::geography, {geo_origin}) / 1000.0 / %s
                    )
                    ELSE 1.0
                  END
            ) AS match_score
        FROM jobs_listing l
        WHERE l.status = 'published'
          AND l.skill_embedding IS NOT NULL
          {country_clause}
        ORDER BY match_score DESC
        LIMIT %s
    """

    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
