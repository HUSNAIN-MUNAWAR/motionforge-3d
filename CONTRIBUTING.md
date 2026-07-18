# Contributing

Thanks for taking the time to improve MotionForge 3D. This project is built around reproducible movement analytics, clear evidence, and honest limitations.

## Development Setup

```bash
python -m pip install -e ".[dev,postgres,queue,storage]"
cd apps/web && npm install
```

Use `.env.example` for local configuration. Never commit `.env`, private media, generated tokens, local databases, model binaries, object-storage volumes, or credentials.

## Pull Request Expectations

- Keep changes focused and explain the user or developer impact.
- Add tests for behavior changes.
- Update docs when formulas, workflows, endpoints, environment variables, or limitations change.
- Run the relevant checks before opening a PR:

```bash
python -m ruff check apps packages scripts tests
python -m ruff format --check apps packages scripts tests
python -m mypy apps packages
python -m pytest -q
cd apps/web && npm run typecheck && npm run build
```

## Analytics Changes

Movement templates and scoring changes need extra care:

- Version movement templates.
- Document formula changes and coordinate assumptions.
- Include controlled fixtures or tests when practical.
- Avoid unmeasured performance, clinical, security, or production-readiness claims.

## Security

Do not report vulnerabilities with private videos, credentials, or personal data in public issues. Follow [SECURITY.md](SECURITY.md).
