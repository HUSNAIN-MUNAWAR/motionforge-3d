"use client";

import { FormEvent, useEffect, useState } from "react";
import { Shell } from "@/components/Shell";
import { apiJson, authHeaders } from "@/lib/api";

type Subject = {id:string;display_name:string;external_reference:string|null;tags:string[];consent_status:string;archived:boolean};
export default function Subjects() {
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [error, setError] = useState("");
  const load = () => apiJson<Subject[]>("/api/v1/subjects", {headers:authHeaders()}).then(setSubjects).catch((e:Error)=>setError(e.message));
  useEffect(() => { void load(); }, []);
  async function create(event:FormEvent<HTMLFormElement>) {
    event.preventDefault(); setError(""); const form=event.currentTarget; const data=new FormData(form);
    try { await apiJson("/api/v1/subjects", {method:"POST",headers:authHeaders({"Content-Type":"application/json"}),body:JSON.stringify({display_name:data.get("display_name"),external_reference:data.get("external_reference")||null,dominant_side:data.get("dominant_side")||null,consent_status:data.get("consent_status")})}); form.reset(); load(); } catch(e){setError((e as Error).message)}
  }
  return <Shell><div className="eyebrow">Participant registry</div><h1>Subjects</h1><div className="grid" style={{gridTemplateColumns:"minmax(280px,.55fr) minmax(0,1fr)"}}><form className="card stack" onSubmit={create}><h3>New anonymous subject</h3><label>Display code<input name="display_name" required placeholder="ATH-001" /></label><label>External reference<input name="external_reference" /></label><label>Dominant side<select name="dominant_side"><option value="">Not specified</option><option>left</option><option>right</option></select></label><label>Consent<select name="consent_status"><option value="not_recorded">Not recorded</option><option value="recorded">Recorded</option><option value="withdrawn">Withdrawn</option></select></label>{error&&<p className="error">{error}</p>}<button className="btn">Create subject</button></form><div className="card"><table className="table"><thead><tr><th>Code</th><th>External ref</th><th>Consent</th><th>Tags</th></tr></thead><tbody>{subjects.map(subject=><tr key={subject.id}><td>{subject.display_name}</td><td>{subject.external_reference||"—"}</td><td><span className="badge">{subject.consent_status}</span></td><td>{subject.tags.join(", ")||"—"}</td></tr>)}</tbody></table>{!subjects.length&&!error&&<p className="muted">No subjects in this organization yet.</p>}</div></div></Shell>;
}
