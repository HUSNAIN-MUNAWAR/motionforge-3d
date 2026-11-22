from pathlib import Path

import cv2

from packages.pose_core import ColorMarkerPoseEstimator, process_video


def test_process_video_writes_real_annotated_video_and_trace(tmp_path: Path):
    result = process_video(
        Path("tests/fixtures/controlled_squat.mp4"),
        ColorMarkerPoseEstimator(),
        session_id="artifact-test",
        artifact_dir=tmp_path / "artifacts",
        sample_fps=8.0,
        annotated_output=tmp_path / "annotated.mp4",
        trace_output=tmp_path / "trace.csv",
    )

    annotated = tmp_path / "annotated.mp4"
    trace = tmp_path / "trace.csv"
    assert annotated.exists() and annotated.stat().st_size > 0
    assert trace.exists() and trace.read_text(encoding="utf-8").count("\n") > 1
    assert result["annotated_path"] == str(annotated)
    assert len(result["trace_rows"]) == result["quality"]["valid_pose_frames"]

    cap = cv2.VideoCapture(str(annotated))
    try:
        assert cap.isOpened()
        assert int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) == 96
    finally:
        cap.release()
