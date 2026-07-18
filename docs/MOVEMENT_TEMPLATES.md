# Movement Templates

Templates live in `configs/movements/*.json` and are versioned. Each declares a primary signal, joint family, required landmarks, signal inversion, peak prominence, duration limits, target range, and posture threshold. Formula changes require a version bump and regression test.

Implemented templates: squat, bicep curl, shoulder raise, and sit-to-stand.
