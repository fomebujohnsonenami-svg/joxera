import { useParams } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { ProfileTimeline } from "../../components/profile/ProfileTimeline";
import { CountryBadge } from "../../components/profile/CountryBadge";
import { Badge } from "../../components/ui/Badge";
import { LoadingSpinner } from "../../components/ui/LoadingSpinner";
import { usePublicProfile } from "../../hooks/useProfile";

export function PublicProfilePage() {
  const { t } = useTranslation();
  const { handle } = useParams<{ handle: string }>();
  const { data: profile, isLoading, isError } = usePublicProfile(handle!);

  if (isLoading) return <LoadingSpinner label={t("common.loading")} />;

  if (isError || !profile) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-16 text-center">
        <p className="text-red-400">{t("common.error")}</p>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto px-4 py-8">
      <header className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <h1 className="text-3xl font-bold">@{profile.handle}</h1>
          <Badge variant={profile.isVerified ? "success" : "warning"}>
            {profile.isVerified
              ? t("profile.verified")
              : t("profile.unverified")}
          </Badge>
        </div>
        <p className="text-xl text-slate-300">{profile.displayName}</p>
        <div className="mt-3">
          <CountryBadge
            countryCode={profile.country}
            verified={profile.isVerified}
            showName
          />
        </div>
        {profile.bio && (
          <p className="text-slate-400 mt-4 leading-relaxed">{profile.bio}</p>
        )}
      </header>

      <section className="mb-8">
        <h2 className="text-lg font-semibold mb-4">{t("profile.credentials")}</h2>
        <ProfileTimeline credentials={profile.credentials} />
      </section>

      {profile.references.length > 0 && (
        <section>
          <h2 className="text-lg font-semibold mb-4">{t("profile.references")}</h2>
          <ul className="space-y-3">
            {profile.references.map((ref) => (
              <li
                key={ref.id}
                className="rounded-lg border border-slate-800 px-4 py-3 text-sm"
              >
                <p className="text-slate-300">{ref.text}</p>
                <p className="text-slate-500 mt-1">
                  — {ref.author} · {ref.rating}/5
                </p>
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}
