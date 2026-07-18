# Troubleshooting

- `MoveNet model not found`: run `make model` on a networked machine and set the model path.
- `No pose detected`: verify the production backend, whole-body framing, codec, and confidence threshold.
- `Duplicate media`: the same SHA-256 already exists inside the active organization.
- `403 Organization access denied`: send the organization ID where the authenticated user has membership.
- `Video decoding validation failed`: transcode to H.264 MP4 and retry.
- Web build cannot resolve packages: remove `apps/web/node_modules` and `apps/web/.next`, run `npm ci`, then rerun `npm run typecheck && npm run build`. The packaged verification build passed with Node 22.16.0.
