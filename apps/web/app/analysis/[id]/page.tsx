"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Shell } from "@/components/Shell";
import { PoseScene } from "@/components/PoseScene";
import { API, authHeaders } from "@/lib/api";

export default function Analysis({ params }: { params: { id: string } }) {
  const id = params.id;
  const [pose, setPose] = useState<any>();
  const [analysis, setAnalysis] = useState<any>();
  const [cursor, setCursor] = useState(0);
  const [videoUrl, setVideoUrl] = useState<string>();
  const [evidenceUrl, setEvidenceUrl] = useState<string>();
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    const demo = id === "demo";
    let videoObject: string | undefined;
    let evidenceObject: string | undefined;
    const poseRequest = fetch(
      demo ? "/demo/pose.json" : `${API}/api/v1/analysis/${id}/pose`,
      demo ? undefined : { headers: authHeaders() },
    ).then((r) => {
      if (!r.ok) throw new Error("Pose unavailable");
      return r.json();
    });
    const analysisRequest = fetch(
      demo ? "/demo/analysis.json" : `${API}/api/v1/analysis/${id}`,
      demo ? undefined : { headers: authHeaders() },
    ).then((r) => {
      if (!r.ok) throw new Error("Analysis unavailable");
      return r.json();
    });
    Promise.all([poseRequest, analysisRequest])
      .then(([p, a]) => {
        setPose(p);
        setAnalysis(a);
      })
      .catch(console.error);
    if (demo) {
      setVideoUrl("/demo/video.webm");
      setEvidenceUrl("/demo/evidence.jpg");
    } else {
      fetch(`${API}/api/v1/analysis/${id}/source`, { headers: authHeaders() })
        .then((r) => (r.ok ? r.blob() : Promise.reject()))
        .then((blob) => {
          videoObject = URL.createObjectURL(blob);
          setVideoUrl(videoObject);
        })
        .catch(() => {});
      fetch(`${API}/api/v1/analysis/${id}/evidence`, { headers: authHeaders() })
        .then((r) => (r.ok ? r.blob() : Promise.reject()))
        .then((blob) => {
          evidenceObject = URL.createObjectURL(blob);
          setEvidenceUrl(evidenceObject);
        })
        .catch(() => {});
    }
    return () => {
      if (videoObject) URL.revokeObjectURL(videoObject);
      if (evidenceObject) URL.revokeObjectURL(evidenceObject);
    };
  }, [id]);

  const frames = pose?.frames || [];
  const frame = frames[Math.min(cursor, Math.max(0, frames.length - 1))];
  const chart = useMemo(() => {
    const t = analysis?.analytics?.timestamps || [];
    const v = analysis?.analytics?.series?.left_knee || analysis?.analytics?.series?.left_elbow || [];
    return t.map((x: number, i: number) => ({ t: Number(x.toFixed(2)), value: v[i] }));
  }, [analysis]);

  function seek(index: number) {
    setCursor(index);
    const target = frames[index]?.timestamp_s;
    if (videoRef.current && typeof target === "number") videoRef.current.currentTime = target;
  }

  function syncVideo() {
    const t = videoRef.current?.currentTime ?? 0;
    if (!frames.length) return;
    let best = 0;
    let bestD = Infinity;
    frames.forEach((f: any, i: number) => {
      const d = Math.abs(f.timestamp_s - t);
      if (d < bestD) {
        best = i;
        bestD = d;
      }
    });
    setCursor(best);
  }

  const isDemo = id === "demo";

  return (
    <Shell>
      <div className="eyebrow">Public dataset analysis workspace</div>
      <h1>{isDemo ? "Wikimedia squat movement analysis" : "Synchronized movement review"}</h1>
      {isDemo && (
        <p className="muted">
          CC BY 3.0 Wikimedia Commons sample attributed to FitnessScape. Public demo data only.
        </p>
      )}
      <div className="workspace">
        <div className="grid">
          <section className="panel">
            <div className="panelHead">
              <b>Source & synchronized cursor</b>
              <span className="badge">{analysis?.coordinate_system || "camera-relative 3D"}</span>
            </div>
            <div className="panelBody">
              <video ref={videoRef} className="video" controls src={videoUrl} onTimeUpdate={syncVideo} />
              <input
                aria-label="Playback position"
                type="range"
                min={0}
                max={Math.max(0, frames.length - 1)}
                value={cursor}
                onChange={(e) => seek(Number(e.target.value))}
                style={{ width: "100%", marginTop: 12 }}
              />
              <div className="muted">
                Frame {frame?.frame_index ?? 0} · {frame?.timestamp_s?.toFixed(2) ?? "0.00"} s
              </div>
            </div>
          </section>
          <section className="panel">
            <div className="panelHead">
              <b>Primary joint signal</b>
              <span className="muted">chart, video and skeleton share one timestamp</span>
            </div>
            <div className="timeline">
              <ResponsiveContainer>
                <LineChart
                  data={chart}
                  onClick={(e: any) => {
                    if (e?.activeTooltipIndex != null) seek(e.activeTooltipIndex);
                  }}
                >
                  <XAxis dataKey="t" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="value" dot={false} stroke="#42e8ff" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </section>
        </div>
        <div className="grid">
          <section className="panel">
            <div className="panelHead">
              <b>3D skeleton</b>
              <span className="badge">actual processed pose frames</span>
            </div>
            <div className="canvas">
              <PoseScene frame={frame} />
            </div>
          </section>
          <section className="panel">
            <div className="panelHead">
              <b>Explainable result</b>
            </div>
            <div className="panelBody grid" style={{ gridTemplateColumns: "1fr 1fr" }}>
              <div className="card">
                <div className="muted">Score</div>
                <div className="metric">{analysis?.analytics?.score?.final ?? "-"}</div>
              </div>
              <div className="card">
                <div className="muted">Repetitions</div>
                <div className="metric">{analysis?.analytics?.repetitions?.length ?? 0}</div>
              </div>
              <div className="card">
                <div className="muted">Confidence</div>
                <div className="metric">{analysis?.quality_metrics?.average_landmark_confidence ?? "-"}</div>
              </div>
              <div className="card">
                <div className="muted">Valid frames</div>
                <div className="metric">{analysis?.quality_metrics?.valid_pose_frames ?? 0}</div>
              </div>
            </div>
          </section>
          <section className="panel">
            <div className="panelHead">
              <b>Evidence</b>
            </div>
            <img
              alt="Actual pose overlay evidence"
              src={evidenceUrl || ""}
              style={{ display: "block", width: "100%" }}
            />
          </section>
        </div>
      </div>
    </Shell>
  );
}
