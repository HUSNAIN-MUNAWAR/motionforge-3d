import Link from "next/link";

export function Shell({children}:{children:React.ReactNode}) {
  return <div className="shell"><aside className="sidebar"><div className="brand">MOTIONFORGE <b>3D</b></div><div className="muted" style={{marginTop:6,fontSize:12}}>Human Movement Intelligence</div><nav className="nav"><Link href="/">Overview</Link><Link href="/dashboard">Dashboard</Link><Link href="/subjects">Subjects</Link><Link href="/sessions">Sessions</Link><Link href="/analysis/demo">Analysis</Link><Link href="/login">Sign in</Link></nav><div className="card" style={{marginTop:28}}><div className="eyebrow">Analysis mode</div><div style={{marginTop:8}}>CPU-first · explainable</div><p className="muted" style={{fontSize:12}}>Monocular output is clearly labelled camera-relative. Metric distance requires calibration.</p></div></aside><main className="main">{children}</main></div>;
}
