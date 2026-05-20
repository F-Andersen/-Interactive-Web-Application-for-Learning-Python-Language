import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

export function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ username: "", email: "", password: "" });
  const [error, setError] = useState("");

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    setError("");
    try {
      await register(form.username, form.email, form.password);
      navigate("/login");
    } catch {
      setError("Не вдалося створити акаунт");
    }
  };

  return (
    <main className="auth-screen">
      <form className="auth-panel" onSubmit={submit}>
        <h1>New student</h1>
        <label>Username<input value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} /></label>
        <label>Email<input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} /></label>
        <label>Password<input type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} /></label>
        {error && <p className="error">{error}</p>}
        <button>Register</button>
        <Link to="/login">Back to login</Link>
      </form>
    </main>
  );
}
