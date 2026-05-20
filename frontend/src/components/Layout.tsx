import { BookOpen, LogOut, Shield, UserCircle } from "lucide-react";
import { Link, NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

export function Layout({ children }: { children: React.ReactNode }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  return (
    <div className="app-shell">
      <header className="topbar">
        <Link to="/courses" className="brand"><BookOpen size={20} /> Python Learn</Link>
        <nav>
          <NavLink to="/courses">Courses</NavLink>
          <NavLink to="/profile"><UserCircle size={16} /> Profile</NavLink>
          {user?.role.name === "admin" && <NavLink to="/admin"><Shield size={16} /> Admin</NavLink>}
        </nav>
        <button
          className="icon-btn"
          title="Logout"
          onClick={() => {
            logout();
            navigate("/login");
          }}
        >
          <LogOut size={18} />
        </button>
      </header>
      <main className="content">{children}</main>
    </div>
  );
}
