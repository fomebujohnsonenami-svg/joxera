import { MetricBox } from "../ui/MetricBox";
import { Badge } from "../ui/Badge";
import type { PaymentRail, WalletData } from "../../types";

const RAIL_LABELS: Record<PaymentRail, string> = {
  MobileMoney: "Mobile Money",
  Pix: "Pix",
  SEPA: "SEPA",
  ACH: "ACH",
  UPI: "UPI",
  SWIFT: "SWIFT",
  Card: "Card",
};

interface WalletBalanceProps {
  wallet: WalletData;
  lockedEscrowTotal?: string;
}

export function WalletBalance({ wallet, lockedEscrowTotal }: WalletBalanceProps) {
  const balance = parseFloat(wallet.balance);
  const locked = lockedEscrowTotal ? parseFloat(lockedEscrowTotal) : 0;

  return (
    <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <MetricBox
        label="Available balance"
        value={`${wallet.currency} ${balance.toLocaleString(undefined, { minimumFractionDigits: 2 })}`}
        hint={`Payout rail: ${RAIL_LABELS[wallet.rail] ?? wallet.rail}`}
        className="sm:col-span-2 lg:col-span-1"
      />
      {locked > 0 && (
        <MetricBox
          label="Locked in escrow"
          value={`${wallet.currency} ${locked.toLocaleString(undefined, { minimumFractionDigits: 2 })}`}
          hint="Released when both parties sign off"
        />
      )}
      <div className="flex items-center gap-2 rounded-md border border-border bg-surface-elevated p-5">
        <Badge>{wallet.currency}</Badge>
        <Badge variant="success">{RAIL_LABELS[wallet.rail] ?? wallet.rail}</Badge>
      </div>
    </div>
  );
}
