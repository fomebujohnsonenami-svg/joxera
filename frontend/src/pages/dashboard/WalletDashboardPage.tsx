import { useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import { LoadingSpinner } from "../../components/ui/LoadingSpinner";
import { EscrowTimelineList } from "../../components/wallet/EscrowTimeline";
import { TransactionHistory } from "../../components/wallet/TransactionHistory";
import { WalletBalance } from "../../components/wallet/WalletBalance";
import { useReleaseEscrow, useWalletDashboard } from "../../hooks/useWallet";
import { useAuth } from "../../hooks/useAuth";

export function WalletDashboardPage() {
  const { t } = useTranslation();
  const { user } = useAuth();
  const { data, isLoading, isError, refetch } = useWalletDashboard();
  const releaseEscrow = useReleaseEscrow();
  const [signOffId, setSignOffId] = useState<number | null>(null);

  const signOffIds = useMemo(() => {
    if (!data || !user) return new Set<number>();
    return new Set(
      data.escrows
        .filter((e) => {
          if (e.state !== "locked") return false;
          const isEmployer = e.employer_handle === user.handle;
          const isTalent = e.talent_handle === user.handle;
          if (isEmployer && !e.employer_signed_off) return true;
          if (isTalent && !e.talent_signed_off) return true;
          return false;
        })
        .map((e) => e.id)
    );
  }, [data, user]);

  const handleSignOff = async (escrowId: number) => {
    setSignOffId(escrowId);
    try {
      await releaseEscrow.mutateAsync(escrowId);
    } finally {
      setSignOffId(null);
    }
  };

  if (isLoading) return <LoadingSpinner label={t("common.loading")} />;

  if (isError || !data) {
    return (
      <div className="text-center py-12">
        <p className="text-red-400 mb-4">{t("common.error")}</p>
        <button
          onClick={() => refetch()}
          className="text-joxera-400 hover:underline text-sm"
        >
          {t("common.retry")}
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-10">
      <header>
        <h1 className="text-2xl font-bold font-heading text-content-primary">
          {t("wallet.title")}
        </h1>
        <p className="mt-2 text-sm text-content-secondary">{t("wallet.subtitle")}</p>
      </header>

      <section aria-label={t("wallet.balanceSection")}>
        <WalletBalance
          wallet={data.wallet}
          lockedEscrowTotal={data.locked_escrow_total}
        />
      </section>

      <section>
        <h2 className="text-lg font-semibold font-heading mb-4 text-content-primary">
          {t("wallet.escrowTimeline")}
        </h2>
        <EscrowTimelineList
          timelines={data.escrow_timelines}
          onSignOff={handleSignOff}
          isSigningOff={releaseEscrow.isPending}
          signOffEscrowId={signOffId}
          canSignOffIds={signOffIds}
        />
      </section>

      <section>
        <h2 className="text-lg font-semibold font-heading mb-4 text-content-primary">
          {t("wallet.transactions")}
        </h2>
        <TransactionHistory transactions={data.transactions} />
      </section>
    </div>
  );
}
