import { FlowStep, FlowSteps } from "../ui/FlowStep";
import { Button } from "../ui/Button";
import { Badge } from "../ui/Badge";
import type { EscrowTimeline } from "../../types";

const STATE_VARIANT: Record<string, "default" | "success" | "warning"> = {
  pending: "warning",
  locked: "default",
  released: "success",
  refunded: "default",
};

interface EscrowTimelineCardProps {
  timeline: EscrowTimeline;
  onSignOff?: (escrowId: number) => void;
  isSigningOff?: boolean;
  canSignOff?: boolean;
}

export function EscrowTimelineCard({
  timeline,
  onSignOff,
  isSigningOff,
  canSignOff,
}: EscrowTimelineCardProps) {
  return (
    <article className="rounded-md border border-border bg-surface-elevated p-5">
      <div className="flex flex-wrap items-start justify-between gap-3 mb-5">
        <div>
          <h3 className="font-heading text-base font-semibold text-content-primary">
            {timeline.listing_title}
          </h3>
          <p className="mt-1 text-sm text-content-muted font-mono tabular-nums">
            {timeline.currency}{" "}
            {parseFloat(timeline.amount).toLocaleString(undefined, { minimumFractionDigits: 2 })}
          </p>
        </div>
        <Badge variant={STATE_VARIANT[timeline.state] ?? "default"}>
          {timeline.state}
        </Badge>
      </div>

      <FlowSteps aria-label={`Escrow lifecycle for ${timeline.listing_title}`}>
        {timeline.steps.map((step, idx) => (
          <FlowStep
            key={step.key}
            step={idx + 1}
            title={step.title}
            description={step.description}
            status={step.status}
            isLast={idx === timeline.steps.length - 1}
          />
        ))}
      </FlowSteps>

      {canSignOff && timeline.state === "locked" && onSignOff && (
        <div className="mt-4 pt-4 border-t border-border">
          <Button
            onClick={() => onSignOff(timeline.escrow_id)}
            disabled={isSigningOff}
            className="w-full sm:w-auto"
          >
            {isSigningOff ? "Signing off…" : "Sign off on completed work"}
          </Button>
        </div>
      )}
    </article>
  );
}

interface EscrowTimelineListProps {
  timelines: EscrowTimeline[];
  onSignOff?: (escrowId: number) => void;
  isSigningOff?: boolean;
  signOffEscrowId?: number | null;
  canSignOffIds?: Set<number>;
}

export function EscrowTimelineList({
  timelines,
  onSignOff,
  isSigningOff,
  signOffEscrowId,
  canSignOffIds,
}: EscrowTimelineListProps) {
  if (timelines.length === 0) {
    return (
      <p className="text-sm text-content-muted py-6 text-center rounded-md border border-dashed border-border">
        No active escrows. Funds appear here when an employer locks payment for your work.
      </p>
    );
  }

  return (
    <div className="space-y-4">
      {timelines.map((timeline) => (
        <EscrowTimelineCard
          key={timeline.escrow_id}
          timeline={timeline}
          onSignOff={onSignOff}
          isSigningOff={isSigningOff && signOffEscrowId === timeline.escrow_id}
          canSignOff={canSignOffIds?.has(timeline.escrow_id)}
        />
      ))}
    </div>
  );
}
