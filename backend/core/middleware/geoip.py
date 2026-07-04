import logging

from django.conf import settings
from django.contrib.gis.geoip2 import GeoIP2, GeoIP2Exception

logger = logging.getLogger(__name__)


def _get_client_ip(request) -> str | None:
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


class GeoIPMiddleware:
    """
    Resolves the requester's ISO 3166-1 alpha-2 country code from their IP
    and attaches it to ``request.country``.

    Resolution order:
    1. ``X-Joxera-Country`` header (dev / explicit override)
    2. MaxMind GeoLite2 lookup via django.contrib.gis.geoip2
    3. ``DEFAULT_COUNTRY`` setting fallback
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self._geoip: GeoIP2 | None = None
        self._geoip_available: bool | None = None

    def __call__(self, request):
        request.country = self.resolve_country(request)
        request.country_detected_via = getattr(
            request, "_country_detected_via", "fallback"
        )
        return self.get_response(request)

    def _get_geoip(self) -> GeoIP2 | None:
        if self._geoip_available is False:
            return None
        if self._geoip is not None:
            return self._geoip
        try:
            self._geoip = GeoIP2()
            self._geoip_available = True
        except (GeoIP2Exception, FileNotFoundError) as exc:
            logger.warning("GeoIP2 database unavailable: %s", exc)
            self._geoip_available = False
            self._geoip = None
        return self._geoip

    def resolve_country(self, request) -> str:
        default = getattr(settings, "DEFAULT_COUNTRY", "US")

        override = request.META.get("HTTP_X_JOXERA_COUNTRY", "").strip().upper()
        if len(override) == 2 and override.isalpha():
            request._country_detected_via = "header"
            return override

        ip = _get_client_ip(request)
        if ip and ip not in ("127.0.0.1", "::1"):
            geoip = self._get_geoip()
            if geoip:
                try:
                    code = geoip.country_code(ip)
                    if code:
                        request._country_detected_via = "geoip"
                        return code.upper()
                except GeoIP2Exception as exc:
                    logger.debug("GeoIP lookup failed for %s: %s", ip, exc)

        request._country_detected_via = "fallback"
        return default.upper()
