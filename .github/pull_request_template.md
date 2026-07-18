## Summary

-

## Validation

- [ ] `python -m ruff check apps packages scripts tests`
- [ ] `python -m ruff format --check apps packages scripts tests`
- [ ] `python -m mypy apps packages`
- [ ] `python -m pytest -q`
- [ ] `cd apps/web && npm run typecheck && npm run build`

## Notes

- Uses only synthetic or approved demo data.
- Does not add secrets, private media, generated databases, model binaries, or local artifacts.
