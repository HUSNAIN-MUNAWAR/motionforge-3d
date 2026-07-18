"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { API } from "@/lib/api";

export default function Onboarding() {
  const router = useRouter();
  const [error, setError] = useState("");
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    const response = await fetch(`${API}/api/v1/organizations`, {
      method: "POST",
      headers: { Authorization: `Bearer ${localStorage.getItem("mf_token") || ""}`, "Content-Type": "application/json" },
      body: JSON.stringify({ name: data.get("name"), slug: data.get("slug") }),
    });
    const payload = await response.json();
    if (!response.ok) return setError(payload.detail || "Organization setup failed");
    localStorage.setItem("mf_org", payload.id);
    router.push("/dashboard");
  }
  return <main className="authPage"><form className="authCard" onSubmit={submit}><div className="eyebrow">Organization onboarding</div><h1>Create your workspace</h1><label>Organization name<input name="name" required /></label><label>URL slug<input name="slug" required pattern="[a-z0-9-]+" placeholder="performance-lab" /></label>{error && <p className="error">{error}</p>}<button className="btn" type="submit">Create organization</button></form></main>;
}
