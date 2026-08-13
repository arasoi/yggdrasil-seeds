# Architecture

> What this repository is, how a seed gets from a directory here onto somebody's
> control plane, and which decisions are made where.
>
> This repository holds **data**. There is no Go here, no Makefile, no build.
> Everything that reads, validates, packs or installs a seed lives in the
> Yggdrasil control-plane repository; this one supplies the bundles and the
> branch model that decides which channel they land on.

## The two repositories, and a third

| Repository | Visibility | Holds | Publishes |
|---|---|---|---|
| `arasoi/yggdrasil` | private | The control plane, the agent, `internal/seed`, `ygg-seed`, and the **embedded** seed set at `seeds/library` | Nothing directly — its CI pushes to the releases repo |
| `arasoi/yggdrasil-seeds` | **public** | This repository: seed bundles under `seeds/` | The seed catalog, one release tag per channel |
| `arasoi/yggdrasil-releases` | public | Nothing authored — a publish target only | `yggd`, `ygg-agent`, `ygg-seed`, `SHA256SUMS` |

The visibility split is the reason this repository carries its own copy of the
format specification rather than linking to it. An author here cannot open the
private repository, and a specification nobody can read is not one.

It is also why CI here **downloads** `ygg-seed` rather than building it:
building would need a read credential for a private repository sitting in a
public repository's CI, which is exactly the credential this whole arrangement
exists to avoid.

## Why seeds are separate at all

A seed is data, not code, so adding or fixing a game should never require a new
control-plane release. Before the split it did: the only way a fix to a bundled
seed reached an operator was a new `yggd` binary, which meant either bumping the
software's version because a YAML file changed, or letting the shipped seeds
drift behind the repository.

So seeds have their own release channel and **each seed carries its own
`version:`**, independent of the software's. Two consequences worth holding onto:

- Fixing a seed does not imply the software changed.
- Releasing the software does not imply any seed changed.

## Two seed sets, and which one you are editing

There are two collections of seeds, and they are not the same thing:

| | `seeds/` here | `seeds/library` upstream |
|---|---|---|
| Reaches an operator by | Downloading from a catalog | Being compiled into the `yggd` binary |
| Updated by | Pushing to this repository | A new control-plane release |
| Exists so that | A seed can be fixed on its own schedule | A fresh install has seeds **with no network at all** |

The embedded set is the offline floor. It is not a mirror of this repository and
is not kept in sync with it: promoting a seed into it is a deliberate commit
upstream, not a sync, and it should stay small for that reason.

**The two sets can hold different versions of the same seed, and the catalog
wins.** Merging is by id and whole-seed, with the catalog layer above the bundled
one — so an installed catalog bundle replaces the embedded copy entirely,
*including when the embedded copy is newer*. A seed fixed upstream but not
published here is therefore not merely unpublished: for any operator who has
installed it from the catalog, the fix is shadowed by the older bundle. That is
why a seed change upstream has to be pushed here too.

Newly authored seeds face no wire-shape restriction in either set. The
compatibility test upstream is scoped to seeds that *had* a schema 2 form and
must keep installing the way they always did; a seed authored directly in schema
3 has nothing to preserve and is compared against nothing. Vintage Story is the
worked example — a two-download install (a .NET runtime and the game), which
sits in both sets.

If you are unsure which set you are editing: this repository is the one whose
bundles sit directly under `seeds/<id>/`, with no `library/` in the path.

## How a seed reaches an operator

```
  seeds/<id>/seed.yaml           you edit this, on a feature branch
        │
        │  merge to develop / qa / main
        ▼
  .github/workflows/publish.yml  the branch IS the channel
        │
        ├─ fetch ygg-seed        from the releases repo, checksum-verified
        ├─ validate              the same loader yggd uses. A gate
        ├─ lint                  advice. Never a gate
        └─ pack                  <id>-<version>.tar.gz, seeds.json, SHA256SUMS
        │
        ▼
  release tag  seeds-<channel>-latest        floating: replaced, never appended
        │
        │  a control plane with seed_channel set reads seeds.json
        ▼
  Seeds page   install / update
        │
        ├─ download the bundle
        ├─ verify against SHA256SUMS
        ├─ stage, then validate through the ordinary loader
        └─ swap into place, and reload in-process — no yggd restart
```

Two properties of that pipeline are worth naming, because they are what make it
safe to publish from a push:

**Packing runs to completion before anything on the remote is touched.** The
packer loads every bundle through the real loader and refuses a version that
cannot be ordered. A catalog nobody could install therefore fails while the
existing release is still intact. Deleting the release first and *then*
discovering the bundles are unpublishable would leave the channel empty, which is
worse than not having published.

**An install is staged, validated, and only then swapped.** A malformed bundle
fails at download with the operator's working copy untouched.

## The channels

| Branch | Release tag | Prerelease | Meaning |
|---|---|---|---|
| `develop` | `seeds-develop-latest` | yes | Edge |
| `qa` | `seeds-qa-latest` | yes | Promoted from develop, under test |
| `main` | `seeds-release-latest` | no | Stable |

**The branch is the channel**, and that is the reason publishing lives in CI here
rather than behind the control plane's own Publish button. That button takes its
channel from a *setting*, which has nothing to do with what is checked out — so a
catalog built from `develop` could be published to the stable channel with
nothing to prevent it, and promotion by merge would mean nothing. Here, merging
`develop` → `qa` → `main` *is* the promotion.

**Each tag floats**: publishing deletes and recreates it, so there is exactly one
catalog per channel and it is always current.

That is also why **a release tag has exactly one writer**. Two producers feeding
one floating tag clobber each other on every push, and the loser is whichever ran
second. CI in this repository is the writer for these tags, which is why
`seeds.publish_repo` should be left **unset** on every control plane — that keeps
the UI's Publish button inert rather than making it a second writer aimed at
these same tags.

## Where a seed sits on a control plane

Seeds load in three layers, each winning entirely over the one before it:

| Layer | Where | Why it is at this level |
|---|---|---|
| bundled | embedded in the `yggd` binary | a fresh install has seeds with no network |
| **catalog** | `<data_dir>/seeds/<id>/` | **this repository** — updated on its own schedule |
| operator | `<seeds-dir>/<id>/` | hand-authored, so a catalog update can never overwrite it |

Merging is by `id`, whole-seed. Two seeds sharing an id are the same seed, and
the higher layer replaces the lower one completely — there is no field-level
merge.

The operator layer sitting **above** the catalog is deliberate: an update
replaces a bundle wholesale, and that operation must be structurally incapable of
reaching hand-written content. Downloaded bundles therefore land in the data
directory rather than in the operator's own seeds directory.

Each installed bundle carries a `.ygg-source.json` recording the channel,
version and digest it came from — inside the bundle rather than in a database, so
a seed and its provenance cannot be separated. Never author that file; the
catalog owns it.

## Trust

Downloading a bundle is HTTPS plus the published `SHA256SUMS`. There is
deliberately **no signing key**, unlike agent binaries.

The reasoning is blast radius. An agent binary executes with Docker-socket access
on every node in a fleet, so it gets real cryptographic verification. A seed is
parsed and validated by the ordinary loader before it can replace anything, and
its contents were already operator-supplied data at this trust level.

`seeds.json` itself is fetched without a checksum, for the same reason: it is a
listing, never executed, and every bundle it names is still checksum-verified.

One consequence for authors: **a seed's install steps run on somebody else's
node**. A `download` step's URL is fetched there, and a `steamcmd` step pulls a
depot there. Publishing a seed is asking every operator who installs it to run
those steps, so treat a URL you did not choose carefully — see
[conventions.md](conventions.md).

## What this repository deliberately does not do

- **Build or test anything.** There is no Go module here. `ygg-seed` is a
  released binary, downloaded when needed.
- **Publish a single seed.** A catalog is an index plus its bundles, so
  publishing one seed means republishing the whole tag.
- **Auto-update anything.** A seed changing under an operator with nobody
  watching would alter what future servers are built from. Installing and
  updating are always an operator's decision.
- **Mirror `seeds/library`.** See "Two seed sets" above.
