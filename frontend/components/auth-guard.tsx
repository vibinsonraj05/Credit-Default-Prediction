
"use client";

import { useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";

export function AuthGuard({
  children,
}: {
  children: React.ReactNode;
}) {
  const [ready, setReady] = useState(false);
  const path = usePathname();
  const router = useRouter();

  useEffect(() => {
    // Normalize GitHub Pages basePath and trailing slash
    const normalizedPath = path
      .replace(/^\/Credit-Default-Prediction(?=\/|$)/, "")
      .replace(/\/+$/, "") || "/";

    const isLoginPage = normalizedPath === "/login";

    const token = sessionStorage.getItem("credi_token");

    if (!isLoginPage && !token) {
      router.replace("/login");
      return;
    }

    if (isLoginPage && token) {
      router.replace("/");
      return;
    }

    setReady(true);
  }, [path, router]);

  if (!ready) {
    return (
      <div
        style={{
          minHeight: "100vh",
          display: "grid",
          placeItems: "center",
          color: "#667085",
        }}
      >
        Loading secure workspace...
      </div>
    );
  }

  return <>{children}</>;
}
