import type { ReactNode } from "react";

export interface NavItem {
  id: string;
  label: string;
  href: string;
  icon?: ReactNode;
  isActive?: boolean;
  external?: boolean;
}

export interface NavSection {
  id: string;
  label: string;
  items: NavItem[];
}

export type CalloutVariant = "info" | "warning" | "success";

export type PillVariant = "mvp" | "v2" | "future";

export interface TagChip {
  id: string;
  label: string;
}
