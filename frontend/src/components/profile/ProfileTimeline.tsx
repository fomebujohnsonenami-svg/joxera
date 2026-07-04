import { useState } from "react";
import { useTranslation } from "react-i18next";
import { Badge } from "../ui/Badge";
import { FlowStep, FlowSteps } from "../ui/FlowStep";
import { Pill } from "../ui/Pill";
import { referencesApi } from "../../services/api/references";
import type { ProofOfWorkCredential } from "../../types";

interface ProfileTimelineProps {
  credentials: ProofOfWorkCredential[];
}

function truncateHash(hash: string, len = 12): string {
  if (hash.length <= len * 2 + 3) return hash;
  return `${hash.slice(0, len)}…${hash.slice(-len)}`;
}

function CredentialBlock({ cred }: { cred: ProofOfWorkCredential }) {
  const { t } = useTranslation();
  const [verifyState, setVerifyState] = useState<"idle" | "loading" | "valid" | "invalid">("idle");

  const handleVerify = async () => {
    setVerifyState("loading");
    try {
      const result = await referencesApi.verify(cred.id);
      setVerifyState(result.valid ? "valid" : "invalid");
    } catch {
      setVerifyState("invalid");
    }
  };

  const completedDate = new Date(cred.completedAt).toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });

  return (
    <article
      className="relative rounded-md border border-border bg-surface-elevated overflow-hidden"
      aria-label={`${cred.jobTitle} credential`}
    >
      <div className="absolute left-0 top-0 bottom-0 w-1 bg-emerald/60" aria-hidden="true" />

      <div className="p-5 pl-6">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <h3 className="font-heading text-base font-semibold text-content-primary">
              {cred.jobTitle}
            </h3>
            <p className="mt-1 text-sm text-content-secondary">
              {t("profile.signedBy", { employer: cred.signedBy })}
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <Pill variant="mvp" label={cred.field.replace(/-/g, " ")} />
            <Badge variant="default">{cred.tier}</Badge>
          </div>
        </div>

        <dl className="mt-4 grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs font-mono">
          <div>
            <dt className="text-content-muted uppercase tracking-wider">{t("profile.completed")}</dt>
            <dd className="text-content-primary mt-0.5">{completedDate}</dd>
          </div>
          <div>
            <dt className="text-content-muted uppercase tracking-wider">{t("profile.signatureHash")}</dt>
            <dd className="text-content-primary mt-0.5 break-all" title={cred.signatureHash}>
              {truncateHash(cred.signatureHash)}
            </dd>
          </div>
        </dl>

        <div className="mt-4 flex flex-wrap items-center gap-3 pt-4 border-t border-border">
          <button
            type="button"
            onClick={handleVerify}
            disabled={verifyState === "loading"}
            className="text-xs font-medium text-accent hover:underline disabled:opacity-50"
          >
            {verifyState === "loading"
              ? t("profile.verifying")
              : t("profile.verifySignature")}
          </button>
          {verifyState === "valid" && (
            <Badge variant="success">{t("profile.verifiedCredential")}</Badge>
          )}
          {verifyState === "invalid" && (
            <Badge variant="warning">{t("profile.invalidCredential")}</Badge>
          )}
          <span className="text-[10px] text-content-muted ml-auto">{t("profile.immutable")}</span>
        </div>
      </div>
    </article>
  );
}

export function ProfileTimeline({ credentials }: ProfileTimelineProps) {
  const { t } = useTranslation();

  if (credentials.length === 0) {
    return (
      <p className="text-sm text-content-muted py-6 text-center rounded-md border border-dashed border-border">
        {t("profile.noCredentials")}
      </p>
    );
  }

  return (
    <div>
      <FlowSteps aria-label={t("profile.credentialsTimeline")} className="mb-6">
        <FlowStep
          step={1}
          title={t("profile.timelineTitle")}
          description={t("profile.timelineDescription")}
          status="complete"
          isLast
        />
      </FlowSteps>

      <ol className="space-y-4" aria-label={t("profile.credentials")}>
        {credentials.map((cred, idx) => (
          <li key={cred.id}>
            <CredentialBlock cred={cred} />
            {idx < credentials.length - 1 && (
              <div className="flex justify-center py-1" aria-hidden="true">
                <div className="h-4 w-px bg-border" />
              </div>
            )}
          </li>
        ))}
      </ol>
    </div>
  );
}
