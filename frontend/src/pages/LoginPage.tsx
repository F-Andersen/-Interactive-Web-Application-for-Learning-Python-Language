import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

export function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ login: "student@example.com", password: "student123" });
  const [error, setError] = useState("");

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    setError("");
    try {
      await login(form.login, form.password);
      navigate("/courses");
    } catch {
      setError("Невірний логін або пароль");
    }
  };

  return (
    <main className="auth-screen">
      <form className="auth-panel" onSubmit={submit}>
        <h1>Python Learn</h1>
        <label>Email або username<input value={form.login} onChange={(e) => setForm({ ...form, login: e.target.value })} /></label>
        <label>Password<input type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} /></label>
        {error && <p className="error">{error}</p>}
        <button>Login</button>
        <Link to="/register">Create account</Link>
      </form>
    </main>
  );
}
