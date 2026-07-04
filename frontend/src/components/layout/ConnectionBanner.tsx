import { useTranslation } from "react-i18next";
import { useOnlineStatus } from "../../hooks/useOnlineStatus";

export function ConnectionBanner() {
  const { t } = useTranslation();
  const { isOnline, wasOffline } = useOnlineStatus();

  if (isOnline && !wasOffline) return null;

  return (
    <div
      className={`text-center text-sm py-2 px-4 ${
        isOnline
          ? "bg-emerald-900/40 text-emerald-300"
          : "bg-amber-900/40 text-amber-200"
      }`}
      role="status"
    >
      {isOnline ? t("common.reconnected") : t("common.offline")}
    </div>
  );
}
