"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { API } from "@/lib/api";

export default function Register() {
  const router = useRouter();
  const [error, setError] = useState("");
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    const data = new FormData(event.currentTarget);
    const response = await fetch(`${API}/api/v1/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ display_name: data.get("name"), email: data.get("email"), password: data.get("password") }),
    });
    const payload = await response.json();
    if (!response.ok) return setError(payload.detail || "Registration failed");
    localStorage.setItem("mf_token", payload.access_token);
    router.push("/onboarding");
  }
  return <main className="authPage"><form className="authCard" onSubmit={submit}><div className="brand">MOTIONFORGE <b>3D</b></div><div className="eyebrow">Account setup</div><h1>Create account</h1><label>Display name<input name="name" required minLength={2} /></label><label>Email<input name="email" type="email" required /></label><label>Password<input name="password" type="password" required minLength={10} /></label>{error && <p className="error">{error}</p>}<button className="btn" type="submit">Register</button><p className="muted">Already registered? <Link href="/login">Sign in</Link></p></form></main>;
}
