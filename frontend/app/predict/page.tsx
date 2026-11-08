"use client";
import { useEffect, useState } from "react";
import { Shell } from "@/components/shell";
import { api } from "@/lib/api";
import { ArrowRight, CheckCircle2 } from "lucide-react";

type Customer = { customer_id: number; customer_name: string; credit_limit: number; age: number; education: number; marriage: number };
type Result = { prediction: number; label: string; probability: number; risk: string; model: string; customer_id: number; customer_name: string; historical_actual_default: number };

export default function PredictPage() {
  const [customer, setCustomer] = useState<Customer | null>(null);
  const [result, setResult] = useState<Result | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api<{ user: { id: string } }>("/api/auth/me")
      .then((session) => api<Customer>(`/api/customers/${session.user.id}`))
      .then(setCustomer)
      .catch((err) => setError(err instanceof Error ? err.message : "Could not load customer profile"));
  }, []);

  async function runPrediction() {
    if (!customer) return;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const prediction = await api<Result>(`/api/predict/by-id/${customer.customer_id}`);
      setResult(prediction);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Prediction failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <Shell title="Predict default" subtitle="Your customer profile is matched automatically using the ID linked to your CSV login.">
      <section className="card form-card">
        <h2 className="card-title">Customer profile</h2>
        <p className="card-subtitle">No need to enter the 22 financial features manually. CrediScope retrieves them from the credit dataset using your authenticated customer ID.</p>
        {customer ? (
          <>
            <div className="grid stats-grid" style={{ marginTop: 22 }}>
              <div className="card"><div className="stat-top">Customer name</div><div className="stat-value" style={{ fontSize: 20 }}>{customer.customer_name}</div></div>
              <div className="card"><div className="stat-top">Customer ID</div><div className="stat-value">{customer.customer_id}</div></div>
              <div className="card"><div className="stat-top">Credit limit</div><div className="stat-value" style={{ fontSize: 20 }}>{customer.credit_limit.toLocaleString()}</div></div>
              <div className="card"><div className="stat-top">Age</div><div className="stat-value">{customer.age}</div></div>
            </div>
            <button className="btn" onClick={runPrediction} disabled={loading} style={{ marginTop: 22 }}>
              {loading ? "Analyzing customer…" : "Predict my default risk"}<ArrowRight size={15}/>
            </button>
          </>
        ) : !error ? <div className="empty">Loading your customer profile…</div> : null}
        {error && <div className="error" style={{ marginTop: 16 }}>{error}</div>}
      </section>

      {result && (
        <section className="result-card" style={{ marginTop: 20 }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 15, flexWrap: "wrap" }}>
            <div><div className="eyebrow">MODEL ASSESSMENT RESULT</div><h2 style={{ font: "800 20px Manrope", margin: "8px 0" }}>{result.label}</h2><p style={{ color: "#667085", fontSize: 12, margin: 0 }}>Customer {result.customer_id} · {result.customer_name} · {result.model}</p></div>
            <span className={`pill ${result.risk === "High" ? "red" : result.risk === "Moderate" ? "amber" : "green"}`}>{result.risk} risk</span>
          </div>
          <div style={{ marginTop: 22 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}><span style={{ fontSize: 12, color: "#667085" }}>Estimated probability of default</span><strong className="result-number">{(result.probability * 100).toFixed(1)}%</strong></div>
            <div className="result-meter"><div style={{ width: `${result.probability * 100}%` }}/></div>
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: 10, color: "#98a2b3" }}><span>0% · Lower estimated risk</span><span>100% · Higher estimated risk</span></div>
          </div>
          <div className="callout" style={{ marginTop: 18 }}><CheckCircle2 size={18} className="callout-icon"/><div><b style={{ fontSize: 12 }}>Interpretation</b><p>{result.prediction === 1 ? "The model estimates that this customer may default based on patterns learned from historical data." : "The model does not classify this customer as likely to default at the selected threshold."} This is a retrospective dataset demonstration, not a forecast of a real customer's future behaviour or a lending recommendation.</p></div></div>
          <p className="card-subtitle" style={{ marginTop: 12 }}>Historical dataset label (for evaluation only): {result.historical_actual_default === 1 ? "Default" : "No default"}. This label is not used as a model input.</p>
        </section>
      )}
    </Shell>
  );
}
