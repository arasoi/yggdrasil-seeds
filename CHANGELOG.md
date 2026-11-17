# Changelog

What changed in the catalog, newest first. Short on purpose: one line per seed change,
written for an operator, naming the seed and its new version.

Add the entry in the same change that bumps a seed's `version:`. Heading format is
`## <date>`; the publish workflow copies the three newest entries into the GitHub
release notes.

## 2026-11-16

- **ark-survival-ascended 5.9.0** and **ark-survival-evolved 1.5.0**: `map` and `session_name`
  are now per-server controls. A cluster never offers or stores them, so each member keeps
  its own. Needs Yggdrasil 0.74.0 or later to take effect; an older control plane ignores it.
