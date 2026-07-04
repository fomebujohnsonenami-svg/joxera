export function LoadingSpinner({ label }: { label?: string }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-12">
      <div
        className="h-8 w-8 animate-spin rounded-full border-2 border-joxera-500 border-t-transparent"
        role="status"
        aria-label={label ?? "Loading"}
      />
      {label && <p className="text-sm text-slate-400">{label}</p>}
    </div>
  );
}
