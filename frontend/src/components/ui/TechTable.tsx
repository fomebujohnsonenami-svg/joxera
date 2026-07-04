import type { ReactNode } from "react";

export interface TechTableColumn<T> {
  id: string;
  header: string;
  accessor: (row: T) => ReactNode;
  align?: "left" | "center" | "right";
  className?: string;
}

export interface TechTableProps<T> {
  columns: TechTableColumn<T>[];
  data: T[];
  caption?: string;
  emptyMessage?: string;
  getRowKey: (row: T, index: number) => string;
  className?: string;
}

const alignClass = {
  left: "text-left",
  center: "text-center",
  right: "text-right",
};

export function TechTable<T>({
  columns,
  data,
  caption,
  emptyMessage = "No data available.",
  getRowKey,
  className = "",
}: TechTableProps<T>) {
  return (
    <div
      className={`overflow-x-auto rounded-md border border-border ${className}`}
    >
      <table className="w-full min-w-[480px] border-collapse text-sm">
        {caption && <caption className="sr-only">{caption}</caption>}
        <thead>
          <tr className="border-b border-border bg-surface-secondary">
            {columns.map((col) => (
              <th
                key={col.id}
                scope="col"
                className={`px-4 py-3 font-mono text-[10px] font-bold uppercase tracking-widest text-content-muted ${alignClass[col.align ?? "left"]} ${col.className ?? ""}`}
              >
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.length === 0 ? (
            <tr>
              <td
                colSpan={columns.length}
                className="px-4 py-8 text-center text-content-muted"
              >
                {emptyMessage}
              </td>
            </tr>
          ) : (
            data.map((row, rowIndex) => (
              <tr
                key={getRowKey(row, rowIndex)}
                className="border-b border-border-subtle last:border-0 hover:bg-surface-elevated/50 transition-colors"
              >
                {columns.map((col) => (
                  <td
                    key={col.id}
                    className={`px-4 py-3 text-content-secondary ${alignClass[col.align ?? "left"]} ${col.className ?? ""}`}
                  >
                    {col.accessor(row)}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}
