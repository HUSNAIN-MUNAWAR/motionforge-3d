# Public Dataset Demo

## Dataset

- **Title:** Squat - exercise demonstration video
- **Publisher/host:** Wikimedia Commons
- **Author attribution:** FitnessScape
- **Official source:** <https://commons.wikimedia.org/wiki/File:Squat_-_exercise_demonstration_video.webm>
- **License:** Creative Commons Attribution 3.0 Unported
- **License URL:** <https://creativecommons.org/licenses/by/3.0/>
- **Download date:** 2026-07-19
- **Local file:** `data/sample/wikimedia-squat/squat-exercise-demonstration.webm`
- **SHA-256:** `2440985661c3533a4ce78472b0f4577dbdf023aff3f8f9a225bbb5ff8071b1e9`

## Why This Dataset

MotionForge 3D analyzes human movement from video. This sample is a short, openly licensed weighted squat demonstration with a visible full-body movement cycle, making it suitable for CPU pose inference, joint-angle analytics, repetition detection, evidence generation, and report export.

The sample is not a benchmark dataset, patient record, customer record, clinical dataset, or production deployment. It is used only as a reproducible public demo.

## File Format and Size

- Raw format: WebM VP9
- Size: 564,942 bytes
- Resolution: 1280 x 720
- Frame rate: 30 FPS
- Frame count: 213
- Duration: 7.1 seconds

The raw sample is committed because the file is small and the license permits redistribution with attribution.

## Fields Used by MotionForge

The video is mapped to a `MediaAsset` record with:

- `storage_key`
- `original_filename`
- `mime_type`
- `sha256`
- `size_bytes`
- `duration_s`
- `width`
- `height`
- `fps`
- `codec`
- `metadata_json`

The generated demo also seeds synthetic local records for:

- organization
- user
- membership
- subject
- movement session
- processing job
- analysis result
- generated report

These local database records are generated only to exercise the application workflow. They are not real users, customers, patients, or athletes.

## Transformations

The public demo runner:

1. Verifies that the WebM sample exists, or downloads it from Wikimedia Commons.
2. Validates the video through OpenCV.
3. Runs MoveNet SinglePose Lightning through ONNX Runtime CPU execution.
4. Samples the 30 FPS video at 4 FPS.
5. Tracks and filters pose frames.
6. Computes squat joint-angle analytics, repetition segments, symmetry, and explainable score components.
7. Generates an evidence image with the actual pose overlay.
8. Generates a PDF report from the persisted analysis.
9. Writes refreshed frontend demo artifacts.

No manual detections, hand-edited predictions, fabricated metrics, or model training are used.

## Reproduction Commands

```bash
python scripts/models/download_movenet.py --output models/movenet-singlepose-lightning.onnx
PYTHONPATH=.:apps/api python scripts/datasets/download_wikimedia_squat.py
PYTHONPATH=.:apps/api python scripts/datasets/run_wikimedia_squat_demo.py
```

Windows PowerShell:

```powershell
py scripts/models/download_movenet.py --output models/movenet-singlepose-lightning.onnx
$env:PYTHONPATH = ".;apps/api"
py scripts/datasets/download_wikimedia_squat.py
py scripts/datasets/run_wikimedia_squat_demo.py
```

## Generated Outputs

The latest public dataset run produced:

- Processing duration: 47.574 seconds
- Decoded frames: 213
- Analyzed frames: 27
- Valid pose frames: 27
- Average landmark confidence: 0.5372
- Repetitions detected: 2
- Generated rule events: 0
- Explainable score: 80.08
- Runtime: ONNX Runtime 1.27.0

Generated files:

- `docs/public_dataset_results.json`
- `docs/public_dataset_artifacts/pose_sequence.json.gz`
- `docs/public_dataset_artifacts/evidence.jpg`
- `docs/public_dataset_artifacts/public_dataset_report.pdf`
- `apps/web/public/demo/analysis.json`
- `apps/web/public/demo/pose.json`
- `apps/web/public/demo/evidence.jpg`
- `apps/web/public/demo/video.webm`

Generated local databases and storage folders are ignored by Git:

- `public_dataset_demo.db`
- `public_dataset_demo_storage/`

## Privacy and Ethics

The sample is public, openly licensed media from Wikimedia Commons. It does not include private customer data, medical identifiers, credentials, or confidential records. MotionForge 3D does not infer identity and does not claim clinical validity from this sample.

## Removal

To remove generated local outputs:

```bash
rm -rf public_dataset_demo.db public_dataset_demo_storage
```

To remove the committed sample from a fork, delete `data/sample/wikimedia-squat/` and update the README and tests accordingly.
