from __future__ import annotations

import argparse
import hashlib
import urllib.request
from pathlib import Path

DATASET_PAGE = "https://commons.wikimedia.org/wiki/File:Squat_-_exercise_demonstration_video.webm"
DOWNLOAD_URL = (
    "https://upload.wikimedia.org/wikipedia/commons/5/5c/Squat_-_exercise_demonstration_video.webm"
)
SHA256 = "2440985661c3533a4ce78472b0f4577dbdf023aff3f8f9a225bbb5ff8071b1e9"
DEFAULT_OUTPUT = Path("data/sample/wikimedia-squat/squat-exercise-demonstration.webm")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download the CC BY 3.0 Wikimedia Commons squat demo video."
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--force", action="store_true", help="Replace an existing file.")
    args = parser.parse_args()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists() and not args.force:
        digest = sha256_file(args.output)
        if digest == SHA256:
            print(f"Already present: {args.output}")
            print(f"Source: {DATASET_PAGE}")
            print("License: CC BY 3.0, attribution required: FitnessScape")
            return
        raise SystemExit(
            f"Existing file has unexpected SHA-256 {digest}. Use --force to replace it."
        )

    tmp = args.output.with_suffix(args.output.suffix + ".tmp")
    print(f"Downloading {DOWNLOAD_URL}")
    urllib.request.urlretrieve(DOWNLOAD_URL, tmp)
    digest = sha256_file(tmp)
    if digest != SHA256:
        tmp.unlink(missing_ok=True)
        raise SystemExit(f"Hash mismatch: expected {SHA256}, got {digest}")
    tmp.replace(args.output)
    print(f"Saved {args.output}")
    print(f"Source: {DATASET_PAGE}")
    print("License: CC BY 3.0, attribution required: FitnessScape")


if __name__ == "__main__":
    main()
