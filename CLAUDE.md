# Project Context

This repository holds **seed definitions** for [Yggdrasil](https://github.com/arasoi/yggdrasil):
game definitions in YAML describing how to install a game, run it, configure it,
and tell when it is up.

**This repository is data, not code.** There is no Go here, no Makefile, no build
and no test suite. Everything that reads, validates, packs or installs a seed
lives in the private control-plane repository; `ygg-seed` is a released binary,
downloaded when needed.

Always consult the documentation in the `docs/` folder before making changes or
suggestions.

- @docs/architecture.md — How this repo relates to the control plane, and how a seed reaches an operator
- @docs/authoring.md — Writing a seed, end to end
- @docs/testing.md — Verifying one against real infrastructure
- @docs/conventions.md — House style, naming, versioning, what counts as a breaking change
- @docs/publishing.md — Channels, the branch model, release mechanics, recovery
- @docs/contributing.md — Branch strategy, review checklist, keeping the mirrored docs current
- @docs/decisions.md — Decision records (`SEED-NNN`)
- @docs/seed-spec.md — **The seed format (schema 3). Mirrored — do not edit here**
- @docs/seed-fields.md — Generated field index. **Mirrored — do not edit here**
- @docs/catalog-steam.md — Candidate Steam-distributed games worth a seed, tiered by Linux confidence
- @docs/catalog-nonsteam.md — Candidate direct-download/installer games worth a seed, tiered similarly

## Key Rules

1. Before authoring or editing a seed, check `docs/seed-spec.md` for the format
   and `docs/conventions.md` for house style.
2. Before proposing a structural change, check `docs/decisions.md` for prior
   decisions and rationale, and `docs/architecture.md` for how the pieces fit.
3. Keep documentation up to date — if you change a convention or a decision,
   update the relevant doc in the same change.
4. `docs/seed-spec.md` and `docs/seed-fields.md` are **copies** of files in the
   private control-plane repository. Never edit them here; see
   `docs/contributing.md`, "Keeping the mirrored docs current".
5. Always create a branch based on the feature being worked on, and commit after
   each task completion.
6. When in doubt, ask rather than assume.

# Working on seeds

## Validate constantly

`ygg-seed` calls the same loader the control plane does, so a seed it accepts is
a seed `yggd` accepts.

```bash
ygg-seed validate seeds/<id>    # must pass — CI gates on it
ygg-seed lint seeds/<id>        # advice: the rules validation deliberately allows
```

Validate after **each** change rather than at the end. The loader dry-renders
every templated field, so a typo fails the moment it is introduced rather than
three edits later.

## Validation is a weak claim

It proves a seed *loads*. It cannot catch a URL that 404s, a port declared TCP
that is really UDP, a readiness pattern the game never prints, or a stop command
that corrupts the save. All of those are silent, and all of them validate.

So: **never present a seed as working on the strength of validation alone.** Say
what was actually run and what was not. `docs/testing.md` is the manual pass.

## Things that cost operators data

- **Never rename a variable or setting without `renamed_from`.** Stored values
  are keyed by name, so a bare rename silently discards what every operator chose
  and reinstates the default.
- **Bump the seed's `version:` in the same commit as any behaviour change**, and
  never decrease it. A version that does not increase is a change nobody is
  offered; a lower one reads as older and leaves operators stuck.
- **Never commit directly to `develop`, `qa` or `main`.** Every push to those
  three publishes a release channel.

## Evidence, not inference

- Only write a `ready.pattern` you have seen in real output. It is a regexp, not
  a substring.
- Prefer no `crash:` rule to an unverified one — a wrong readiness pattern
  delays a server, a wrong crash pattern stops a healthy one.
- Declare `architectures` from what was confirmed, not from what is assumed.
- Record what was **not** verified, in a comment in the seed. The next person
  reads the seed, not the pull request.

## Comments carry the reasoning

Seeds here are heavily commented, and deliberately so: comments say *why* a value
is what it is and what was actually checked, not what the field already states.
Match the existing bundles.

Do not reference `ADR-NNN` numbers from inside a seed — those live in the private
repository and a reader here cannot follow them. State the reasoning instead.
`docs/decisions.md` is the exception, and uses its own `SEED-NNN` series.

## No secrets

A seed is published to a public repository and downloaded by strangers. Never put
a real credential in one; use `generate: password` for anything secret per
server.

# Version Control

- Write clear, concise commit messages that explain the decision, not the diff.
- One logical change per commit, and one seed per commit where practical.
- Keep pull requests small and focused.

## Branch Strategy

- **main** — stable; publishes `seeds-release-latest`
- **qa** — promoted from develop, under test; publishes `seeds-qa-latest`
- **develop** — integration branch for active development; publishes `seeds-develop-latest`

Every push to those three branches **publishes a catalog**. Feature branches are
created from `develop` and merged back into `develop`; promotion to `qa` and
`main` is by merge.

## Starting a New Feature

Always create a new `feature/<short-feature-description>` branch off `develop`
before starting any new unit of work — proactively, without waiting to be asked.
Never make edits directly on `main`, `develop`, or `qa`.

Before starting work, determine the feature from the request and check the
current branch:

- If currently on `main`/`develop`/`qa`, or on a branch for a different feature,
  commit any uncommitted work first, then create and switch to a new
  `feature/<short-feature-description>` branch.
- Always create a new feature branch when the work belongs to a different feature
  than the current branch represents.

## Finishing a Task

When a discrete unit of work is complete and in a working state, stage the
changed files and create a git commit with a clear, concise message describing
what was accomplished. Do not push — commit locally only, and only if the user
hasn't asked to hold off on committing.
