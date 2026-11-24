import numpy as np
import pytest

from packages.pose_core.processing import _write_evidence_image


def test_pose_evidence_write_failure_is_explicit(tmp_path, monkeypatch):
    monkeypatch.setattr("packages.pose_core.processing.cv2.imwrite", lambda *_args: False)
    with pytest.raises(RuntimeError, match="Could not write pose evidence image"):
        _write_evidence_image(tmp_path / "evidence.jpg", np.zeros((8, 8, 3), dtype=np.uint8))
