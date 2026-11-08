"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Activity, BarChart3, Clock3, LayoutDashboard, ShieldCheck, Sparkles } from "lucide-react";
const links = [{ href: "/", label: "Overview", icon: LayoutDashboard }, { href: "/predict", label: "Predict default", icon: Sparkles }, { href: "/history", label: "Prediction history", icon: Clock3 }, { href: "/model-performance", label: "Model performance", icon: BarChart3 }];
export function Sidebar() {
 const pathname = usePathname();
 return <aside className="sidebar"><div className="brand"><div className="brand-mark"><ShieldCheck size={21}/></div><div><strong>CrediScope</strong><span>RISK INTELLIGENCE</span></div></div><div className="side-label">WORKSPACE</div><nav>{links.map(({href,label,icon:Icon})=><Link key={href} href={href} className={`nav-link ${pathname===href?"active":""}`}><Icon size={18}/>{label}</Link>)}</nav><div className="sidebar-bottom"><div className="secure-icon"><Activity size={17}/></div><div><strong>Model monitoring</strong><p>Local development environment</p></div><span className="status-dot"/></div></aside>
}
