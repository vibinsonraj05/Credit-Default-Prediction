"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";

type LoginResponse = {
  token: string;
  user: { id: string; name: string; email: string };
};

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const router = useRouter();

  async function submit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      const response = await api<LoginResponse>("/api/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });
      sessionStorage.setItem("credi_token", response.token);
      sessionStorage.setItem("credi_user", JSON.stringify(response.user));
      router.replace("/");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="auth-page">
      <form className="card auth-card" onSubmit={submit}>
        <div className="brand-mark" style={{ marginBottom: 18 }}>CS</div>
        <div className="eyebrow">CREDISCOPE · SECURE ACCESS</div>
        <h1>Welcome back</h1>
        <p className="card-subtitle">Sign in using the customer email and password from your credentials dataset.</p>
        <div className="field">
          <label htmlFor="email">Email address</label>
          <input id="email" type="email" autoComplete="username" required value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Customer email" />
        </div>
        <div className="field">
          <label htmlFor="password">Password</label>
          <input id="password" type="password" autoComplete="current-password" required value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Customer password" />
        </div>
        {error && <div className="error">{error}</div>}
        <button className="btn" disabled={busy} style={{ width: "100%", justifyContent: "center" }}>
          {busy ? "Signing in…" : "Sign in"}
        </button>
        <p className="auth-switch">Use the credentials assigned to your customer record. No separate registration is required.</p>
      </form>
    </main>
  );
}
