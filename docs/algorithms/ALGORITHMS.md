# Algorithms and Conventions

## Joint angle

For landmarks `a-b-c`, MotionForge computes the internal angle at `b`:

`theta = acos(clamp(((a-b) dot (c-b)) / (||a-b|| ||c-b||), -1, 1))`

Degenerate segments return `null` rather than an invented value.

## Derivatives

Angular and landmark velocities use `numpy.gradient(values, timestamps)`. Timestamps must be strictly increasing; the code does not assume a constant frame rate.

## Symmetry

For comparable left and right values:

`symmetry_percent = max(0, 100 * (1 - abs(L-R) / max(abs(L), abs(R), epsilon)))`

The raw left/right values remain visible beside the derived percentage.

## Repetition detection

1. Select the template’s primary angle.
2. Use temporally filtered values.
3. Optionally invert the signal.
4. Detect peaks using configurable prominence and minimum distance.
5. Find neighboring valleys, including valid boundary valleys.
6. Reject duration outside template limits.
7. Store start, peak, end, amplitude, duration, and transparent confidence.

No trained action classifier is claimed.

## One Euro filter

The implementation adapts its low-pass cutoff based on the estimated signal derivative. `min_cutoff`, `beta`, `d_cutoff`, and observed sampling frequency are explicit.

## Approximate monocular 3D

Single-camera frames use `camera_plane_3d`: normalized x/y and non-metric z. This is sufficient for synchronized 3D scene playback but is not presented as calibrated depth.

## Calibrated triangulation

Given `P1`, `P2`, corresponding undistorted points, and confidence filtering, OpenCV linear triangulation recovers a homogeneous point. The point is accepted only after reprojection error is below the configured threshold. Unit tests use known cameras and a known world point.
