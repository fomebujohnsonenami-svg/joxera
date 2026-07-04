import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { Button } from "../components/ui/Button";

export function NotFoundPage() {
  const { t } = useTranslation();

  return (
    <div className="max-w-lg mx-auto px-4 py-24 text-center">
      <h1 className="text-6xl font-bold text-slate-700 mb-4">404</h1>
      <p className="text-slate-400 mb-8">{t("errors.notFound")}</p>
      <Link to="/">
        <Button variant="secondary">{t("common.backHome")}</Button>
      </Link>
    </div>
  );
}
