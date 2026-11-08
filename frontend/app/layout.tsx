import type { Metadata } from "next";
import "./globals.css";
import { AuthGuard } from "@/components/auth-guard";
export const metadata: Metadata = { title: "CrediScope | Credit Risk Intelligence", description: "Credit card default prediction and model analytics" };
export default function RootLayout({children}:{children:React.ReactNode}) { return <html lang="en"><body><AuthGuard>{children}</AuthGuard></body></html>; }
