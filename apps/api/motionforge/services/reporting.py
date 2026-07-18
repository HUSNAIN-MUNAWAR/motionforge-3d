from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..config import get_settings
from ..models import AnalysisResult, Organization, Report, Session as MovementSession, Subject


def generate_report(db: Session, session: MovementSession, actor_id: str) -> Report:
    analysis = db.scalar(select(AnalysisResult).where(AnalysisResult.session_id == session.id))
    if not analysis:
        raise ValueError("Analysis has not completed")
    subject = db.get(Subject, session.subject_id)
    org = db.get(Organization, session.organization_id)
    root = get_settings().storage_root / "reports" / session.organization_id
    root.mkdir(parents=True, exist_ok=True)
    path = root / f"{session.id}.pdf"
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(
        str(path),
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
    )
    story = [
        Paragraph("MotionForge 3D — Movement Analysis Report", styles["Title"]),
        Spacer(1, 6),
        Paragraph(
            "Decision-support analytics only. This report is not a medical diagnosis.",
            styles["Italic"],
        ),
        Spacer(1, 12),
    ]
    info = [
        ["Organization", org.name if org else session.organization_id],
        ["Subject", subject.display_name if subject else session.subject_id],
        ["Session", session.title],
        ["Movement template", session.movement_template],
        ["Analysis mode", analysis.coordinate_system],
        ["Generated", datetime.now(timezone.utc).isoformat()],
    ]
    story.append(
        Table(
            info,
            colWidths=[45 * mm, 115 * mm],
            style=TableStyle(
                [
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#e7eef6")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]
            ),
        )
    )
    story += [Spacer(1, 12), Paragraph("Data quality", styles["Heading2"])]
    story.append(
        Table(
            [[k.replace("_", " ").title(), str(v)] for k, v in analysis.quality_metrics.items()],
            colWidths=[70 * mm, 90 * mm],
            style=TableStyle([("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey)]),
        )
    )
    story += [Spacer(1, 12), Paragraph("Movement summary", styles["Heading2"])]
    score = analysis.analytics.get("score", {})
    reps = analysis.analytics.get("repetitions", [])
    story.append(
        Table(
            [
                ["Explainable score", score.get("final")],
                ["Repetitions", len(reps)],
                ["Symmetry", analysis.analytics.get("symmetry_percent")],
            ],
            colWidths=[70 * mm, 90 * mm],
            style=TableStyle([("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey)]),
        )
    )
    summaries = []
    for name, vals in analysis.analytics.get("summaries", {}).items():
        if vals.get("range") is not None:
            summaries.append(
                [
                    name,
                    round(vals["min"], 1),
                    round(vals["max"], 1),
                    round(vals["range"], 1),
                    round(vals["mean"], 1),
                ]
            )
    if summaries:
        story += [
            Spacer(1, 10),
            Table(
                [["Joint", "Min", "Max", "ROM", "Mean"]] + summaries,
                repeatRows=1,
                style=TableStyle(
                    [
                        ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#142033")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ]
                ),
            ),
        ]
    if analysis.evidence_key and Path(analysis.evidence_key).exists():
        story += [
            PageBreak(),
            Paragraph("Evidence", styles["Heading2"]),
            Image(analysis.evidence_key, width=160 * mm, height=90 * mm),
        ]
    story += [
        Spacer(1, 12),
        Paragraph("Limitations", styles["Heading2"]),
        Paragraph(
            "Monocular measurements are camera-relative and not metric. Camera angle, lighting, loose clothing, occlusion, and overlapping people can reduce accuracy. Metric distances require calibration. Review generated findings before operational use.",
            styles["BodyText"],
        ),
    ]
    doc.build(story)
    report = Report(
        organization_id=session.organization_id,
        session_id=session.id,
        storage_key=str(path),
        generated_by=actor_id,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report
