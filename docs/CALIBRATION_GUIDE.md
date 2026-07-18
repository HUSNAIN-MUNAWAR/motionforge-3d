# Calibration Guide

Use a printed chessboard or ChArUco board with known square dimensions. Capture many images that cover the image corners, vary board orientation, and avoid motion blur. Store intrinsic matrix, distortion coefficients, image size, extrinsics, projection matrices, board definition, software version, and mean reprojection error.

The implemented geometry package accepts projection matrices and performs triangulation/reprojection validation. A complete production capture UI for chessboard/ChArUco extraction remains an extension point; calibration records and tests are present.
