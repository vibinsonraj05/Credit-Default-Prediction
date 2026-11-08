const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
export async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const token = typeof window !== "undefined" ? sessionStorage.getItem("credi_token") : null;
  const response = await fetch(`${API}${path}`, { ...init, headers: { "Content-Type": "application/json", ...(token ? { Authorization: `Bearer ${token}` } : {}), ...init?.headers }, cache: "no-store" });
  if (!response.ok) { const body = await response.json().catch(() => ({})); throw new Error(body.detail || `API request failed (${response.status})`); }
  return response.json();
}
export type Metrics = { dataset_rows: number; feature_count: number; default_rate: number; best_model: string; models: { model: string; accuracy: number; precision: number; recall: number; f1: number; roc_auc: number; confusion_matrix: number[][] }[] };
