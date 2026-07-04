import { createBrowserRouter, Navigate } from "react-router-dom";
import { CountryGuard } from "../components/routing/CountryGuard";
import { ProtectedRoute } from "../components/routing/ProtectedRoute";
import { AuthLayout } from "../layouts/AuthLayout";
import { DashboardLayout } from "../layouts/DashboardLayout";
import { RootLayout } from "../layouts/RootLayout";
import { LoginPage } from "../pages/auth/LoginPage";
import { RegisterPage } from "../pages/auth/RegisterPage";
import { AuthCallbackPage } from "../pages/auth/AuthCallbackPage";
import { EmployerDashboardPage } from "../pages/dashboard/EmployerDashboardPage";
import { TalentDashboardPage } from "../pages/dashboard/TalentDashboardPage";
import { WalletDashboardPage } from "../pages/dashboard/WalletDashboardPage";
import { JobDetailPage } from "../pages/jobs/JobDetailPage";
import { JobFeedPage } from "../pages/jobs/JobFeedPage";
import { PostJobPage } from "../pages/jobs/PostJobPage";
import { LandingPage } from "../pages/LandingPage";
import { NotFoundPage } from "../pages/NotFoundPage";
import { PublicProfilePage } from "../pages/profile/PublicProfilePage";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <RootLayout />,
    errorElement: <NotFoundPage />,
    children: [
      { index: true, element: <LandingPage /> },

      {
        path: "auth",
        element: <AuthLayout />,
        children: [
          { path: "login", element: <LoginPage /> },
          { path: "register", element: <RegisterPage /> },
          { path: "callback", element: <AuthCallbackPage /> },
        ],
      },

      {
        path: "dashboard",
        element: (
          <ProtectedRoute>
            <DashboardLayout />
          </ProtectedRoute>
        ),
        children: [
          { index: true, element: <Navigate to="talent" replace /> },
          { path: "talent", element: <TalentDashboardPage /> },
          { path: "employer", element: <EmployerDashboardPage /> },
          { path: "wallet", element: <WalletDashboardPage /> },
          { path: "employer/post", element: <PostJobPage /> },
        ],
      },

      { path: "profile/:handle", element: <PublicProfilePage /> },

      {
        path: ":country",
        element: <CountryGuard />,
        children: [
          { path: "jobs", element: <JobFeedPage /> },
          { path: "jobs/:id", element: <JobDetailPage /> },
        ],
      },

      { path: "*", element: <NotFoundPage /> },
    ],
  },
]);
