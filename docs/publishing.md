# Publishing

> How a merge here becomes a catalog somebody's control plane can install from,
> what to do when it goes wrong, and the rules that keep the channels coherent.
>
> The pipeline itself is `.github/workflows/publish.yml`, which is commented at
> length. This is the operator's view of it.

## The branch is the channel

| Branch | Release tag | Prerelease | Meaning |
|---|---|---|---|
| `develop` | `seeds-develop-latest` | yes | Edge |
| `qa` | `seeds-qa-latest` | yes | Promoted from develop, under test |
| `main` | `seeds-release-latest` | no | Stable |

Pushing to one of those three branches publishes that channel. **Promotion is a
merge** — `develop` → `qa` → `main` — and there is no other mechanism. Nothing
is tagged by hand and no version is typed anywhere.

That mapping is the reason publishing lives here rather than behind the control
plane's Publish button. That button takes its channel from a *setting*, which
has nothing to do with what is checked out, so a catalog built from `develop`
could be published to the stable channel with nothing to prevent it — and
promotion by merge would mean nothing.

## One writer per tag

**A floating release tag has exactly one writer.** Two producers feeding one tag
clobber each other on every push, and the loser is whichever ran second.

CI in this repository is that writer. So on every control plane,
**`seeds.publish_repo` must be left unset** — which keeps the UI's Publish
button inert rather than making it a second writer aimed at these same tags. The
button is not removed, because it is the path for an operator with no CI
publishing a catalog for their own fleet; it is simply not pointed here.

The control plane also refuses to publish to `arasoi/yggdrasil-releases`
outright, as a checked error rather than a warning: that repository carries the
binaries and base images, and a wholesale release replacement aimed at it would
take out the distribution itself with no undo.

## What a publish does

On a push to one of the three branches, touching `seeds/**` or the workflow
itself:

1. **Resolve the channel** from the branch name. An unexpected branch fails.
2. **Fetch `ygg-seed`** from `arasoi/yggdrasil-releases`, verified against the
   published `SHA256SUMS`. Downloaded rather than built: this repository holds
   seeds, not Go source, and the source repository is private — building here
   would put a read credential for a private repository into a public one's CI.
3. **Validate every bundle.** The strict gate, calling the same loader a control
   plane does. A failure here is one that would otherwise have happened on
   somebody's control plane.
4. **Lint every bundle.** Reported, never a gate — these are rules the loader
   deliberately does not enforce, because it is applied to bundles older releases
   wrote.
5. **Pack.** Produces `<id>-<version>.tar.gz` per seed, plus `seeds.json` and
   `SHA256SUMS`.
6. **Publish**, replacing the channel's release.

**Packing runs to completion before anything on the remote is touched.** A
catalog nobody could install fails while the existing release is still intact.
Deleting the release first and then discovering the bundles are unpublishable
would leave the channel empty, which is worse than not having published. The
publish step additionally refuses to replace a tag with an empty catalog.

**The tag is deleted and recreated**, because GitHub will not re-point an
existing release's assets and leaving the old ones behind would publish a
`seeds.json` naming bundles beside stale ones it does not name. Runs on one
branch are queued rather than cancelled, so the older commit never wins.

## Which `ygg-seed` packs

Pinned to `release-latest` by default: the tool that decides what a catalog looks
like should not track edge, whichever branch is being published.

The `PACKER_CHANNEL` repository variable overrides it, and exists for one
situation — a `ygg-seed` change that has not been promoted to `main` yet, where
the packer needed for a seed does not exist on the stable channel. It is a
variable rather than a silent fallback because taking edge without being asked is
the drift the default prevents.

**It should normally be unset.** If you set it, remove it as soon as the change
it was waiting on is promoted, and say so in the commit that sets it.

## What ends up in a release

```
seeds.json                     the index a control plane reads
SHA256SUMS                     every bundle's digest
<id>-<version>.tar.gz          one per seed
```

`seeds.json` carries each seed's id, name, description, icon, version, schema and
architectures, so the Seeds page can list what is available without downloading
anything. It is fetched **without** a checksum — it is a listing, never executed,
and every bundle it names is still verified.

## What an operator does

Nothing in this repository needs cloning. On a control plane:

| Setting | Does |
|---|---|
| `seed_channel` | Which channel to read. **Empty by default** — with it unset the Seeds page makes no outbound call at all |
| `seeds.catalog_repo` | Which repository to read from. Defaults to `arasoi/yggdrasil-seeds` |
| `seeds.publish_repo` | **Leave unset.** See "One writer per tag" |

Installing and updating are the same action, and both end in an in-process
reload — a downloaded seed is usable without restarting `yggd`. The install is
staged, validated through the ordinary loader, and only then swapped into place,
so a malformed entry fails at download with the working copy untouched.

The index is cached in memory for an hour, keyed by repository *and* channel. A
seed you publish will not appear instantly on a control plane that has already
looked.

## Promoting

```bash
git checkout qa && git merge develop && git push     # develop -> qa
git checkout main && git merge qa && git push        # qa -> main
```

Promote deliberately. `develop` is expected to carry seeds that have been
validated and lightly exercised; `main` is what an operator running the stable
channel installs without thinking about it. A seed that has never started a real
server does not belong on `main` — see [testing.md](testing.md).

There is no partial promotion. A merge carries every seed on the branch, because
a catalog is an index plus its bundles and there is no mechanism to publish one
seed.

## When something goes wrong

**A publish failed and the channel is stale.** The previous release is intact —
that is what packing-before-publishing buys. Fix the seed and push again.

**A publish failed and the channel is empty.** Re-run the workflow. If it fails
again, the packer is rejecting something: read the validate step's output, which
names the bundle.

**A wedged run that cannot be re-run.** The workflow carries
`workflow_dispatch`, so it can be triggered by hand from the Actions tab without
an empty commit on a permanent branch.

**A bad seed reached a channel.** There is no unpublish. Fix it forward: correct
the seed, **bump its version**, and push — a version that does not increase is a
version nobody is offered, so a fix at the same version is invisible. Reverting
the commit works as long as the revert also lands with a higher version than the
bad one.

**A seed's version went backwards.** A control plane orders versions and reads a
lower one as "older" rather than offering a downgrade. So an operator who
installed the bad version is stuck until a *higher* version exists. Always fix
forward.

**The published catalog disagrees with what you expect.** Check which branch
published last, and check the release's own notes — they record the branch and
the commit the catalog was built from.

## What is deliberately not built

- **Publishing a single seed.** A catalog is an index plus its bundles.
- **Merging two catalogs.**
- **Any scheduled or automatic publish.** A seed changing under an operator with
  nobody watching alters what future servers are built from.
- **A signing key.** Trust is HTTPS plus `SHA256SUMS` — see
  [architecture.md](architecture.md), "Trust".
