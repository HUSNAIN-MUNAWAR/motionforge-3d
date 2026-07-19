import fs from "node:fs";
import path from "node:path";
import { Shell } from "@/components/Shell";

function loadJson(name: string) {
  return JSON.parse(fs.readFileSync(path.join(process.cwd(), "public", "demo", name), "utf8"));
}

function linePath(values: number[], width = 640, height = 190) {
  const min = Math.min(...values);
  const max = Math.max(...values);
  const span = Math.max(1, max - min);
  return values
    .map((value, index) => {
      const x = (index / Math.max(1, values.length - 1)) * width;
      const y = height - ((value - min) / span) * height;
      return `${index ? "L" : "M"}${x},${y}`;
    })
    .join(" ");
}

const EDGES = [
  ["left_shoulder", "right_shoulder"],
  ["left_shoulder", "left_elbow"],
  ["left_elbow", "left_wrist"],
  ["right_shoulder", "right_elbow"],
  ["right_elbow", "right_wrist"],
  ["left_shoulder", "left_hip"],
  ["right_shoulder", "right_hip"],
  ["left_hip", "right_hip"],
  ["left_hip", "left_knee"],
  ["left_knee", "left_ankle"],
  ["right_hip", "right_knee"],
  ["right_knee", "right_ankle"],
];

export default function Preview() {
  const analysis = loadJson("analysis.json");
  const pose = loadJson("pose.json");
  const frame = pose.frames[Math.floor(pose.frames.length / 2)];
  const values = (analysis.analytics.series.left_knee as Array<number | null>).map((v) => v ?? 0);
  const joints = frame.landmarks as Record<string, { x: number; y: number; confidence: number }>;

  return (
    <Shell>
      <div className="eyebrow">Public dataset artifact preview</div>
      <h1>Wikimedia squat analysis</h1>
      <p className="muted">
        This printable route uses the same MoveNet pose and analytics artifacts loaded by the
        interactive workspace. Public demo data only; source video is CC BY 3.0 attributed to
        FitnessScape.
      </p>
      <div className="workspace">
        <div className="grid">
          <section className="panel">
            <div className="panelHead">
              <b>Evidence frame</b>
              <span className="badge">actual MoveNet overlay</span>
            </div>
            <img alt="Pose evidence" src="/demo/evidence.jpg" style={{ display: "block", width: "100%" }} />
          </section>
          <section className="panel">
            <div className="panelHead">
              <b>Left knee angle</b>
              <span className="muted">{analysis.quality_metrics.valid_pose_frames} analyzed frames</span>
            </div>
            <div className="panelBody">
              <svg viewBox="0 0 640 220" style={{ width: "100%", height: 220 }}>
                <path
                  d={linePath(values)}
                  fill="none"
                  stroke="#42e8ff"
                  strokeWidth="4"
                  transform="translate(0 12)"
                />
                <line x1="0" y1="205" x2="640" y2="205" stroke="#22344a" />
              </svg>
            </div>
          </section>
        </div>
        <div className="grid">
          <section className="panel">
            <div className="panelHead">
              <b>Pose projection</b>
              <span className="badge">frame {frame.frame_index}</span>
            </div>
            <div className="panelBody">
              <svg
                viewBox="0 0 640 480"
                style={{ width: "100%", height: 390, background: "#060b12", borderRadius: 12 }}
              >
                {EDGES.map(([a, b]) =>
                  joints[a] && joints[b] ? (
                    <line
                      key={`${a}-${b}`}
                      x1={joints[a].x * 640}
                      y1={joints[a].y * 480}
                      x2={joints[b].x * 640}
                      y2={joints[b].y * 480}
                      stroke="#42e8ff"
                      strokeWidth="5"
                    />
                  ) : null,
                )}
                {Object.entries(joints).map(([name, j]) => (
                  <circle key={name} cx={j.x * 640} cy={j.y * 480} r="7" fill="#eef7ff" />
                ))}
              </svg>
            </div>
          </section>
          <section className="panel">
            <div className="panelHead">
              <b>Explainable result</b>
            </div>
            <div className="panelBody grid" style={{ gridTemplateColumns: "1fr 1fr" }}>
              <div className="card">
                <div className="muted">Score</div>
                <div className="metric">{analysis.analytics.score.final}</div>
              </div>
              <div className="card">
                <div className="muted">Repetitions</div>
                <div className="metric">{analysis.analytics.repetitions.length}</div>
              </div>
              <div className="card">
                <div className="muted">Valid frames</div>
                <div className="metric">{analysis.quality_metrics.valid_pose_frames}</div>
              </div>
              <div className="card">
                <div className="muted">Confidence</div>
                <div className="metric">{analysis.quality_metrics.average_landmark_confidence}</div>
              </div>
            </div>
          </section>
        </div>
      </div>
    </Shell>
  );
}
