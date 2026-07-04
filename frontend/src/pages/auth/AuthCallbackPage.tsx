import { useEffect, useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useQueryClient } from "@tanstack/react-query";
import { authApi } from "../../services/api/auth";
import { tokenStorage } from "../../services/auth/tokenStorage";
import { AUTH_QUERY_KEY } from "../../hooks/useAuth";
import { LoadingSpinner } from "../../components/ui/LoadingSpinner";

export function AuthCallbackPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const processed = useRef(false);
  const [error, setError] = useState(false);

  useEffect(() => {
    if (processed.current) return;
    processed.current = true;

    const match = window.location.hash.match(/session_id=([^&]+)/);
    if (!match) {
      navigate("/auth/login", { replace: true });
      return;
    }

    const sessionId = decodeURIComponent(match[1]);
    authApi
      .googleSession(sessionId)
      .then((data) => {
        tokenStorage.setTokens(data.access, data.refresh);
        queryClient.setQueryData(AUTH_QUERY_KEY, data.user);
        window.history.replaceState(null, "", "/auth/callback");
        const dest =
          data.user.role === "employer"
            ? "/dashboard/employer"
            : "/dashboard/talent";
        navigate(dest, { replace: true });
      })
      .catch(() => setError(true));
  }, [navigate, queryClient]);

  if (error) {
    return (
      <div className="text-center" data-testid="auth-callback-error">
        <p className="text-red-400 text-sm mb-4">{t("auth.callbackError")}</p>
        <Link to="/auth/login" className="text-joxera-400 hover:underline text-sm">
          {t("nav.login")}
        </Link>
      </div>
    );
  }

  return (
    <div data-testid="auth-callback-loading">
      <LoadingSpinner label={t("auth.callbackProcessing")} />
    </div>
  );
}
