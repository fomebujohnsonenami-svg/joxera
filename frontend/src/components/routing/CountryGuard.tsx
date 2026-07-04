import { Navigate, Outlet } from "react-router-dom";
import { useCountry } from "../../hooks/useCountry";

export function CountryGuard() {
  const { country, isValid } = useCountry();

  if (!country || !isValid) {
    return <Navigate to="/" replace />;
  }

  return <Outlet />;
}
