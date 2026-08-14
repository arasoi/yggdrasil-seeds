# Decision records

> Why this repository is arranged the way it is. Record a decision here when a
> future reader would otherwise re-litigate it.
>
> Not for routine seed changes — a comment in the seed is the right home for
> those, and it is the one a reader actually sees.

## Numbering, and the relationship to the control plane's ADRs

Records here are numbered **`SEED-NNN`**, independently of the `ADR-NNN` series
in the private control-plane repository. Two separate series rather than one
shared one, because the repositories are released separately and a shared
sequence would need a shared allocator.

Where a decision here follows from one made there, it says so and **restates the
reasoning** rather than only citing a number, since a reader of this public
repository cannot open the private one. That is also why seeds themselves must
not reference ADR numbers — see [conventions.md](conventions.md).

## Template

### SEED-NNN: Title

- **Date:** YYYY-MM-DD
- **Status:** Proposed | Accepted | Deprecated | Superseded
- **Context:** What situation prompted this?
- **Decision:** What did we decide?
- **Consequences:** What are the trade-offs?

---

## Decisions

### SEED-001: The catalog has a repository of its own, and this is its only writer

- **Date:** 2026-08-09
- **Status:** Accepted
- **Context:** Seeds needed to be publishable on their own schedule, so that
  fixing a game definition did not require a new `yggd` release and a release did
  not imply any seed changed. The obvious home was the repository that already
  published binaries and container images — and that turns out to be the one
  place it must not be. A catalog is published to a **floating** release tag,
  which means the existing release is deleted and recreated; a publish aimed at
  the binaries repository would therefore take out the distribution itself, with
  no undo.
- **Decision:** The catalog lives in its own public repository,
  `arasoi/yggdrasil-seeds`, separate from both the private source repository and
  the public releases repository. **A release tag has exactly one writer**, and
  for these tags that writer is CI here. The control plane's own Publish button
  stays available — it is the path for an operator with no CI publishing a
  catalog for their own fleet — but `seeds.publish_repo` is left unset on every
  control plane, which keeps it inert rather than making it a second writer
  aimed at these same tags. The control plane additionally refuses the binaries
  repository as a publish target outright, as a checked error rather than a
  warning.
- **Consequences:** Two producers can no longer clobber each other on a shared
  tag, which they would have done on every push with the loser being whichever
  ran second. A repository that is a publish target now holds nothing else worth
  losing. The cost is a third repository to keep track of, and a seed change that
  is no longer visible in the control plane's own history.

---

### SEED-002: The branch is the channel

- **Date:** 2026-08-09
- **Status:** Accepted
- **Context:** Something has to decide which channel a catalog is published to.
  The control plane's publisher reads it from a *setting*, which has nothing to
  do with what is checked out — so a catalog built from `develop` could be
  published to the stable channel with nothing to prevent it, and promotion would
  be an assertion rather than a mechanism.
- **Decision:** Publishing happens in CI here, and the branch name *is* the
  channel: `develop` → `seeds-develop-latest`, `qa` → `seeds-qa-latest`, `main` →
  `seeds-release-latest`. Promotion is a merge and nothing else. An unexpected
  branch fails the workflow rather than guessing.
- **Consequences:** Branch and channel cannot disagree, and `develop` → `qa` →
  `main` means exactly what it does in the source repository. Publishing to this
  repository's own releases needs only the built-in token, so there is **no
  personal access token** to mint, store, rotate or leak — which is most of why
  the branch model is worth having.

  The costs are real and both follow from the same property. Every push to one of
  those three branches is a release, so there is no "merge now, publish later";
  and there is no partial promotion, because a catalog is an index plus its
  bundles and a merge carries every seed on the branch.

---

### SEED-003: Bundles sit directly under `seeds/`, and this is not the embedded set

- **Date:** 2026-08-09
- **Status:** Accepted
- **Context:** There are two collections of seeds. One is compiled into the
  `yggd` binary so that a fresh install has seeds with no network at all; the
  other is this repository, downloaded on its own schedule. Giving both the same
  path would invite treating one as a mirror of the other.
- **Decision:** Bundles here live at `seeds/<id>/`, with no `library/` segment —
  the embedded set upstream keeps `seeds/library/<id>/`. The two are
  **independent**: promoting a seed into the embedded set is a deliberate commit
  upstream, not a sync, and the copies then drift.
- **Consequences:** The path alone says which set you are editing. An operator
  installing from the catalog gets a seed that overrides the embedded copy
  entirely, since merging is by id and whole-seed. The cost is that a seed
  existing in both places has two copies that can disagree — accepted, because
  the embedded set should stay small and is meant to be an offline floor rather
  than a current mirror.

---

### SEED-004: The embedded set carries a wire-shape constraint this repository does not

- **Date:** 2026-08-12
- **Status:** **Superseded by SEED-010**
- **Context:** Adding the Vintage Story seed appeared to force this into the
  open. Its Linux server tarball is not self-contained and needs a .NET runtime,
  which the plain base image deliberately does not carry — so the install is
  **two** downloads, and a compatibility test upstream appeared to require every
  *bundled* seed's install to survive conversion to the older single-download
  wire shape.
- **Decision:** The seed lives here and not in the embedded set, because a
  two-file install cannot be expressed in the legacy shape.
- **Why it was wrong:** The test is scoped to seeds that *had* a schema 2 form
  and must keep installing the way they always did. A seed authored directly in
  schema 3 has no earlier form to preserve and is compared against nothing, so
  it was never excluded — the test simply needed scoping correctly, which is
  what happened upstream when Vintage Story was promoted into `seeds/library`.
  See SEED-010 for what is actually true, and for what turned out to matter more.

---

---

### SEED-005: The format specification is mirrored here, not linked

- **Date:** 2026-08-13
- **Status:** Accepted
- **Context:** The control-plane repository is **private** and this one is
  **public**. The specification, and the generated field index, live next to the
  Go package that defines the format — so this repository's README linked to
  them there, which is a dead link for every reader who is not the owner. A
  specification nobody can open is not one.
- **Decision:** Carry verbatim copies at [seed-spec.md](seed-spec.md) and
  [seed-fields.md](seed-fields.md), each with a header saying it is a mirror,
  where the original is, and that paths like `internal/seed` and every ADR
  reference point at a repository the reader cannot see. Both are refreshed by
  copying, never edited here; [contributing.md](contributing.md) carries the
  procedure and the staleness test.
- **Consequences:** An author has the format in the repository they are working
  in. The cost is a copy that can fall behind, which is why the header says how
  to tell: `ygg-seed validate` accepting a field the index does not list means
  the mirror is stale, and the tool is always the authority. Verbatim rather than
  adapted, deliberately — an adapted copy would diverge in ways that read as
  intentional, where a verbatim one only ever lags.

---

### SEED-006: CI downloads `ygg-seed` rather than building it

- **Date:** 2026-08-09
- **Status:** Accepted
- **Context:** Publishing needs the packer, which is Go source in the private
  repository. Building it here would put a read credential for a private
  repository into a public repository's CI — the same class of long-lived secret
  the branch model was chosen to avoid.
- **Decision:** Download the published `ygg-seed-linux-amd64` from the releases
  repository and verify it against the published `SHA256SUMS`. Pinned to the
  stable channel by default, since the tool that decides what a catalog looks
  like should not track edge whichever branch is being published. The
  `PACKER_CHANNEL` repository variable overrides it, for the one case where a
  needed packer change has not been promoted yet — a variable rather than a
  silent fallback, because taking edge without being asked is the drift the
  default prevents.
- **Consequences:** No credential to manage. Trust is HTTPS plus a published
  checksum, which is the same level an operator is told to use for `yggd` itself
  and the same one a control plane applies to these very bundles. The cost is
  that the packer's own version is now a thing that can be wrong, and an override
  that is easy to leave set — so it should be removed as soon as the change it
  was waiting on is promoted.

---

### SEED-007: Validation gates; lint advises

- **Date:** 2026-08-09
- **Status:** Accepted
- **Context:** Two kinds of check exist. One answers "will this load", which an
  operator's control plane will also answer, and the other is advice about
  judgement — a stale version, a `backup.include` naming nothing, a crash rule
  at all. Folding the advice into the gate would make every new piece of it
  something that can break a publish, and the loader is applied to bundles older
  releases wrote, so tightening it is a migration rather than a bugfix.
- **Decision:** `ygg-seed validate` is a gate in CI and fails the publish.
  `ygg-seed lint` is reported and never fails it. Packing is a second, stricter
  gate: it loads every bundle through the real loader and refuses a version that
  cannot be ordered.
- **Consequences:** A bundle that would fail on somebody's control plane fails
  here instead, on the change that broke it. New advice can be added freely
  without breaking anybody's publish. The cost is that lint output must actually
  be read, since nothing enforces it — hence its place on the review checklist.

---

### SEED-008: Packing runs to completion before the remote is touched

- **Date:** 2026-08-09
- **Status:** Accepted
- **Context:** A floating tag is replaced by deleting and recreating the release,
  because GitHub will not re-point an existing release's assets and leaving the
  old ones behind would publish an index naming bundles beside stale ones it does
  not name. Deleting first and then discovering the bundles are unpublishable
  would leave the channel **empty**.
- **Decision:** Validate, lint and pack all run first. Only once a complete
  catalog exists on disk is the release deleted and recreated, and the publish
  step additionally refuses to replace a tag with an empty catalog. Concurrent
  runs on one branch are queued rather than cancelled, so the older commit never
  wins a race.
- **Consequences:** A failed publish leaves the previous catalog intact and
  installable, which is the difference between a stale channel and a broken one.
  There is still a brief window between delete and create in which the channel
  does not exist; accepted, since it is bounded by one API call and the
  alternative needs a publishing model GitHub releases do not offer.

---

### SEED-009: There are no automated tests here, and verification is manual

- **Date:** 2026-08-13
- **Status:** Accepted
- **Context:** This repository holds data, not code, so the usual answer — a test
  suite — has nothing to run against. What actually needs proving is that a game
  installs, starts, accepts a connection and shuts down without corrupting its
  save, and that requires a real control plane, a real agent, a real container
  daemon and enough disk for the game. The control plane's mock fleet cannot
  stand in: it runs over a fake runtime, so it never pulls an image, never runs
  an install step, never starts a game, and strips readiness rules outright.
- **Decision:** CI checks that every bundle **loads and packs**, and nothing
  more. Everything beyond that is a documented manual pass —
  [testing.md](testing.md) — carried out by the author before opening a pull
  request, with what was and was not verified recorded in the seed as a comment
  and in the PR description.
- **Consequences:** CI stays fast, needs no infrastructure, and makes no claim it
  cannot support. The honest cost is that the strongest automated guarantee is
  "this document is well-formed" — a seed with the wrong port protocol validates,
  lints clean, packs and publishes. That is precisely why the convention is to
  record what was not verified: the gap is real, it is not going to be closed by
  CI, and a reader deserves to know which parts of a seed are attested and which
  are inference.

---

### SEED-010: A seed in both sets must be published here, because the catalog shadows the binary

- **Date:** 2026-08-13
- **Status:** Accepted (supersedes SEED-004)
- **Context:** SEED-004 claimed the embedded set was closed to installs the
  legacy wire shape could not express, and used Vintage Story's two-download
  install as proof. That was wrong, and finding out why exposed something more
  important.

  The compatibility test upstream is **scoped** to seeds that had a schema 2
  form: those must keep installing exactly as they always did, so their installs
  are compared before and after conversion. A seed authored directly in schema 3
  has no earlier form to preserve and is compared against nothing. Vintage Story
  was never excluded — the test needed scoping correctly, which is what happened
  when the seed was promoted into `seeds/library` upstream.

  So a seed can live in **both** sets. And the layering makes that a hazard
  rather than a nicety: bundled < catalog < operator, so an installed catalog
  bundle replaces the embedded copy **entirely, including when the embedded copy
  is newer**. Observed live — the embedded copy of Vintage Story reached 2.0.0
  upstream while the catalog here was still on 1.1.1, which means every operator
  who had installed it from the catalog was pinned to the older seed by the very
  act of having installed it. Not a stale copy sitting harmlessly in a private
  repository: an active override.
- **Decision:** There is no wire-shape restriction on a newly authored seed in
  either set. A seed may live in both, and when it does, **a change upstream must
  be published here too, at a version at least as high.** Neither the packer nor
  any test can catch a divergence — the two sets are in different repositories,
  and one of them is private — so it is a standing practice, stated in
  [contributing.md](contributing.md) with the two commands that check it, and
  codified upstream as its own rule.
- **Consequences:** "Add it to the bundled set too" is available for any seed,
  which is a real capability SEED-004 wrongly ruled out. In exchange, a seed in
  both sets now has an ongoing obligation, and the failure mode is silent in the
  direction that matters least intuitively: publishing here *always* wins, so
  forgetting to publish is what hurts, and forgetting to promote upstream costs
  only the offline floor being older than the catalog, which is what it is for.

  The scope of that obligation is worth stating plainly, because the record above
  reads as though it concerns one seed: **it concerns all of them.** Every bundle
  in this repository is also in `seeds/library` upstream, byte-identical as of
  Vintage Story 2.0.0. The overlap being total is not a decision — it is simply
  where the two sets have ended up — but it means "is this seed embedded too?"
  has the same answer for every seed here, and that answer is yes.

  Worth keeping as a method note, since it is the second time this has bitten in
  this repository: **the fact that mattered was not the one being checked.** The
  question was "may this seed be embedded", and the answer turned out to be
  irrelevant next to "what happens when it is in both places". A constraint that
  looks like it partitions two sets is worth testing by trying to violate it
  before it is written down as the reason they are separate.
