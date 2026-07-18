"use client";

import { useEffect, useState } from "react";
import { Shell } from "@/components/Shell";
import { apiJson, authHeaders } from "@/lib/api";

type Summary = {sessions_total:number;subjects_total:number;completed_sessions:number;awaiting_review:number;active_jobs:number;failed_jobs:number;average_analysis_confidence:number|null;events_by_severity:Record<string,number>};
export default function Dashboard() {
  const [summary, setSummary] = useState<Summary | null>(null);
  const [error, setError] = useState("");
  useEffect(() => { apiJson<Summary>("/api/v1/dashboard/summary", { headers: authHeaders() }).then(setSummary).catch((e:Error)=>setError(e.message)); }, []);
  const items = [
    ["Sessions", summary?.sessions_total], ["Subjects", summary?.subjects_total], ["Completed", summary?.completed_sessions],
    ["Awaiting review", summary?.awaiting_review], ["Active jobs", summary?.active_jobs], ["Failed jobs", summary?.failed_jobs],
  ];
  return <Shell><div className="eyebrow">Operational command center</div><h1>Dashboard</h1>{error && <p className="error">{error}</p>}<section className="grid cards">{items.map(([label,value])=><div className="card" key={String(label)}><div className="muted">{label}</div><div className="metric">{value ?? "—"}</div></div>)}</section><section className="grid cards"><div className="card"><div className="muted">Average analysis confidence</div><div className="metric">{summary?.average_analysis_confidence ?? "—"}</div></div><div className="card"><div className="muted">Events by severity</div><pre>{JSON.stringify(summary?.events_by_severity ?? {}, null, 2)}</pre></div></section></Shell>;
}
