import { TechTable, type TechTableColumn } from "../ui/TechTable";
import { Badge } from "../ui/Badge";
import type { WalletTransaction } from "../../types";

const TX_LABELS: Record<string, string> = {
  credit: "Credit",
  debit: "Debit",
  escrow_lock: "Escrow lock",
  escrow_release: "Escrow release",
  escrow_refund: "Escrow refund",
  payout: "Payout",
};

const TX_VARIANT: Record<string, "default" | "success" | "warning"> = {
  credit: "success",
  debit: "warning",
  escrow_lock: "warning",
  escrow_release: "success",
  escrow_refund: "default",
  payout: "default",
};

interface TransactionHistoryProps {
  transactions: WalletTransaction[];
}

export function TransactionHistory({ transactions }: TransactionHistoryProps) {
  const columns: TechTableColumn<WalletTransaction>[] = [
    {
      id: "date",
      header: "Date",
      accessor: (row) =>
        new Date(row.created_at).toLocaleDateString(undefined, {
          month: "short",
          day: "numeric",
          year: "numeric",
          hour: "2-digit",
          minute: "2-digit",
        }),
    },
    {
      id: "type",
      header: "Type",
      accessor: (row) => (
        <Badge variant={TX_VARIANT[row.tx_type] ?? "default"}>
          {TX_LABELS[row.tx_type] ?? row.tx_type}
        </Badge>
      ),
    },
    {
      id: "description",
      header: "Description",
      accessor: (row) => (
        <span className="text-content-primary">
          {row.listing_title ?? row.description ?? "—"}
        </span>
      ),
    },
    {
      id: "amount",
      header: "Amount",
      align: "right",
      accessor: (row) => {
        const isCredit = ["credit", "escrow_release", "escrow_refund"].includes(row.tx_type);
        return (
          <span className={isCredit ? "text-emerald font-mono" : "text-content-primary font-mono"}>
            {isCredit ? "+" : "−"}
            {row.currency} {parseFloat(row.amount).toLocaleString(undefined, { minimumFractionDigits: 2 })}
          </span>
        );
      },
    },
    {
      id: "balance",
      header: "Balance after",
      align: "right",
      accessor: (row) => (
        <span className="font-mono text-content-muted tabular-nums">
          {row.currency} {parseFloat(row.balance_after).toLocaleString(undefined, { minimumFractionDigits: 2 })}
        </span>
      ),
    },
  ];

  return (
    <TechTable
      columns={columns}
      data={transactions}
      caption="Wallet transaction history"
      emptyMessage="No transactions yet."
      getRowKey={(row) => String(row.id)}
    />
  );
}
