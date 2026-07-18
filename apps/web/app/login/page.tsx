"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { API } from "@/lib/api";

export default function Login() {
  const router = useRouter();
  const [error, setError] = useState("");
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    const data = new FormData(event.currentTarget);
    const response = await fetch(`${API}/api/v1/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: data.get("email"), password: data.get("password") }),
    });
    const payload = await response.json();
    if (!response.ok) return setError(payload.detail || "Login failed");
    localStorage.setItem("mf_token", payload.access_token);
    router.push(localStorage.getItem("mf_org") ? "/dashboard" : "/onboarding");
  }
  return <main className="authPage"><form className="authCard" onSubmit={submit}><div className="brand">MOTIONFORGE <b>3D</b></div><div className="eyebrow">Secure workspace</div><h1>Sign in</h1><label>Email<input name="email" type="email" required /></label><label>Password<input name="password" type="password" minLength={10} required /></label>{error && <p className="error">{error}</p>}<button className="btn" type="submit">Continue</button><p className="muted">No account? <Link href="/register">Create one</Link></p></form></main>;
}
