# yggdrasil-seeds

Seed definitions for [Yggdrasil](https://github.com/arasoi/yggdrasil), the game
server manager. A **seed** is a game definition: how to install a game, how to
run it, what an operator can configure, and how to tell when it is up.

This repository is the source of truth for them. `seeds/` holds the bundles;
each release tag carries the packed catalog a control plane downloads.

## Installing a seed

Nothing here needs to be cloned. In Yggdrasil, open **Seeds**, choose a channel,
and install what you want — bundles are downloaded, checksum-verified, validated
and swapped into place without restarting `yggd`.

| Channel | Release tag | What it is |
|---|---|---|
| `main` | `seeds-release-latest` | Stable |
| `qa` | `seeds-qa-latest` | Promoted from develop, under test |
| `develop` | `seeds-develop-latest` | Edge |

Each tag floats: publishing replaces it, so there is exactly one catalog per
channel and it is always current. A control plane reading a different repository
sets `seeds.catalog_repo` in its settings.

## What is in a bundle

```
seeds/<id>/
  seed.yaml       # the manifest
  configs/        # config-file templates, if the seed renders any
  icon.png        # branding, if it ships any
```

The format is schema 3, specified in [docs/seed-spec.md](docs/seed-spec.md).
`internal/seed.Validate` in the control plane is normative — the rules that
matter most are cross-field and no schema language expresses them — so the
practical test of any claim in the spec is `ygg-seed validate`, which calls
exactly that code.

Every seed carries its own `version:`, independent of Yggdrasil's. That is the
point of publishing them separately: fixing a seed does not need a new `yggd`
release, and a `yggd` release does not imply any seed changed.

## Contributing a seed

`ygg-seed` is the tool for this, and it will not accept a seed `yggd` would
refuse — it calls the same loader.

```bash
ygg-seed init -id my-game      # scaffolds a bundle that already validates
ygg-seed validate seeds/my-game
ygg-seed lint seeds/my-game    # advice: the rules validation deliberately allows
```

Bump `version:` whenever behaviour changes. Nothing enforces it — the packer can
only reject a version it cannot *order*, not one that is merely stale — and
forgetting means nobody is ever offered the change.

Only write a `ready.pattern` you have seen in real output, and prefer no
`crash:` rule at all to an unverified one: a wrong readiness pattern delays a
server, a wrong crash pattern stops a healthy one.

Validation proves a seed **loads**, which is a much weaker claim than that the
game runs — a port declared TCP that is really UDP validates, lints clean, and
refuses every connection. [docs/testing.md](docs/testing.md) is the pass that
closes that gap; run it before opening a pull request.

## Documentation

| | |
|---|---|
| [authoring.md](docs/authoring.md) | Writing a seed, end to end |
| [testing.md](docs/testing.md) | Verifying one against real infrastructure |
| [conventions.md](docs/conventions.md) | House style, versioning, what counts as a breaking change |
| [contributing.md](docs/contributing.md) | Branches, review checklist |
| [publishing.md](docs/publishing.md) | Channels, the branch model, recovery |
| [architecture.md](docs/architecture.md) | How a seed reaches an operator |
| [decisions.md](docs/decisions.md) | Why things are arranged this way |
| [seed-spec.md](docs/seed-spec.md) · [seed-fields.md](docs/seed-fields.md) | The format. Mirrored from the control-plane repository — do not edit here |
