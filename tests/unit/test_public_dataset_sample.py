from pathlib import Path

import cv2

from scripts.datasets.download_wikimedia_squat import DEFAULT_OUTPUT, SHA256, sha256_file


def test_committed_wikimedia_squat_sample_matches_documented_hash():
    path = Path(DEFAULT_OUTPUT)
    assert path.exists()
    assert sha256_file(path) == SHA256


def test_committed_wikimedia_squat_sample_is_decodable_video():
    cap = cv2.VideoCapture(str(DEFAULT_OUTPUT))
    try:
        assert cap.isOpened()
        assert int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) == 213
        assert int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) == 1280
        assert int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) == 720
    finally:
        cap.release()
