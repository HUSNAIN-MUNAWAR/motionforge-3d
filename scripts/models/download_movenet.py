from __future__ import annotations
import argparse
import hashlib
import urllib.request
from pathlib import Path

URL = "https://huggingface.co/Xenova/movenet-singlepose-lightning/resolve/main/onnx/model.onnx?download=true"
SHA256 = "1ad4f8d6c2f776a9967db3993c9ca740bc350104f9d37c151dc183fc29a464ad"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--output", default="models/movenet-singlepose-lightning.onnx")
    a = p.parse_args()
    out = Path(a.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(URL, out)
    digest = hashlib.sha256(out.read_bytes()).hexdigest()
    if digest != SHA256:
        out.unlink(missing_ok=True)
        raise SystemExit(f"Hash mismatch: {digest}")
    print(out)


if __name__ == "__main__":
    main()
