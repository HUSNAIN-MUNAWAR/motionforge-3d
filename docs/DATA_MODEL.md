# Data Model

Relational tables cover users, organizations, memberships, subjects, sessions, media assets, processing jobs, analysis results, generated events, review annotations, calibrations, reports, and audit events. Every tenant-owned record has an organization ID and useful indexes.

Frame-level landmarks are not expanded into millions of SQL rows. They are stored in a versioned compressed JSON artifact containing timestamps, track ID, coordinate system, unit, landmark confidence/visibility/interpolation flags, raw-versus-filtered status, model metadata, and calibration metadata.
