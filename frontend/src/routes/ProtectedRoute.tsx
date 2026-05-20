import { Navigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

export function ProtectedRoute({ children, adminOnly = false }: { children: JSX.Element; adminOnly?: boolean }) {
  const { user, loading } = useAuth();
  if (loading) return <main className="screen"><div className="panel">Loading...</div></main>;
  if (!user) return <Navigate to="/login" replace />;
  if (adminOnly && user.role.name !== "admin") return <Navigate to="/courses" replace />;
  return children;
}
