"use client";
import { useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
export function AuthGuard({ children }: { children: React.ReactNode }) {
  const [ready, setReady] = useState(false);
  const path = usePathname();
  const router = useRouter();
  useEffect(() => {
    const token = sessionStorage.getItem("credi_token");
    if (path !== "/login" && !token) router.replace("/login");
    else if (path === "/login" && token) router.replace("/");
    else setReady(true);
  }, [path, router]);
  if (!ready) return <div style={{ minHeight: "100vh", display: "grid", placeItems: "center", color: "#667085" }}>Loading secure workspace…</div>;
  return <>{children}</>;
}
