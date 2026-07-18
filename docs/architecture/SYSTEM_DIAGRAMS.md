# System Diagrams

## 1. System context

```mermaid
flowchart LR
  Analyst[Analyst / Coach / Reviewer] --> Web[MotionForge Web]
  Admin[Organization Admin] --> Web
  Web --> API[MotionForge API]
  API --> IdP[Internal identity and RBAC]
  API --> Storage[Protected media and artifacts]
  API --> DB[(Relational database)]
  API --> Queue[(Redis queue)]
  Queue --> Worker[Analysis worker]
```

## 2. Container architecture

```mermaid
flowchart TB
  B[Browser] --> N[Next.js]
  N --> F[FastAPI]
  F --> PG[(PostgreSQL)]
  F --> RD[(Redis)]
  F --> MO[(MinIO / local storage)]
  RD --> CW[Celery worker]
  CW --> CV[OpenCV + model runtime]
  CW --> PG
  CW --> MO
  PR[Prometheus] -. optional .-> F
  GF[Grafana] -. optional .-> PR
```

## 3. Video-processing pipeline

```mermaid
flowchart LR
  U[Validated upload] --> D[Streaming decode]
  D --> S[Frame sampling]
  S --> P[Pose estimation]
  P --> T[Track association]
  T --> Q[Confidence filtering]
  Q --> I[Interpolation]
  I --> O[Outlier handling]
  O --> E[EMA / One Euro]
  E --> A[Angles and derivatives]
  A --> R[Repetitions and phases]
  R --> X[Rules and score]
  X --> V[Evidence + pose artifact + DB summaries]
```

## 4. Database relationship overview

```mermaid
erDiagram
  USER ||--o{ MEMBERSHIP : has
  ORGANIZATION ||--o{ MEMBERSHIP : contains
  ORGANIZATION ||--o{ SUBJECT : owns
  SUBJECT ||--o{ SESSION : has
  SESSION ||--o{ MEDIA_ASSET : contains
  SESSION ||--o{ PROCESSING_JOB : schedules
  SESSION ||--|| ANALYSIS_RESULT : produces
  SESSION ||--o{ GENERATED_EVENT : flags
  SESSION ||--o{ REVIEW_ANNOTATION : receives
  SESSION ||--o{ REPORT : exports
  ORGANIZATION ||--o{ CAMERA_CALIBRATION : owns
  ORGANIZATION ||--o{ AUDIT_EVENT : records
```

## 5. Processing job state machine

```mermaid
stateDiagram-v2
  [*] --> Pending
  Pending --> Queued
  Queued --> Validating
  Validating --> RunningPose
  RunningPose --> Filtering
  Filtering --> Reconstructing3D
  Reconstructing3D --> CalculatingMetrics
  CalculatingMetrics --> DetectingEvents
  DetectingEvents --> ProducingMedia
  ProducingMedia --> Persisting
  Persisting --> Completed
  Queued --> Cancelled
  RunningPose --> Failed
  Persisting --> Failed
```

## 6. Multi-camera calibration and triangulation

```mermaid
flowchart LR
  C1[Camera 1 images] --> K1[Intrinsic calibration]
  C2[Camera 2 images] --> K2[Intrinsic calibration]
  K1 --> E[Extrinsic solve]
  K2 --> E
  E --> P1[Projection matrix P1]
  E --> P2[Projection matrix P2]
  L1[2D landmark camera 1] --> TR[Linear triangulation]
  L2[2D landmark camera 2] --> TR
  P1 --> TR
  P2 --> TR
  TR --> RP[Reprojection validation]
  RP -->|within threshold| W[World 3D point]
  RP -->|outside threshold| RJ[Reject / flag]
```

## 7. Authentication and authorization flow

```mermaid
sequenceDiagram
  participant B as Browser
  participant A as API
  participant D as Database
  B->>A: Login credentials
  A->>D: Lookup user
  A->>A: Argon2 verify
  A-->>B: Expiring JWT
  B->>A: Request + JWT + X-Organization-ID
  A->>D: Validate user and membership
  A->>D: Tenant-scoped query
  A-->>B: Authorized resource or 403
```

## 8. Data-retention flow

```mermaid
flowchart TD
  RP[Retention policy] --> SC[Select expired sessions]
  SC --> DB[Mark deletion pending]
  DB --> OA[Delete object artifacts]
  OA -->|success| MD[Delete or anonymize metadata]
  OA -->|failure| RT[Retry queue + audit]
  MD --> AU[Retain minimum audit record]
```

## 9. Frontend analysis-workspace flow

```mermaid
flowchart LR
  PS[Pose sequence] --> C[Shared playback cursor]
  V[Source video] --> C
  M[Metric series] --> C
  EV[Events and annotations] --> C
  C --> S3[3D skeleton]
  C --> TL[Timeline]
  C --> MP[Metrics panel]
  C --> VD[Video frame]
```

## 10. Deployment architecture

```mermaid
flowchart TB
  IN[Ingress / TLS] --> WEB[Next.js container]
  IN --> API[FastAPI container]
  API --> PG[(Managed PostgreSQL)]
  API --> RD[(Managed Redis)]
  API --> S3[(S3-compatible storage)]
  RD --> W1[Worker replica 1]
  RD --> W2[Worker replica N]
  W1 --> S3
  W2 --> S3
  OT[OpenTelemetry collector] -.-> API
  OT -.-> W1
```
