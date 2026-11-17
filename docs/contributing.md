# Contributing

> The workflow: branches, what a change has to clear, and how the reference docs
> here stay current with the private repository they come from.
>
> New to the format? Start with [authoring.md](authoring.md).

## Branches

| Branch | Is | Publishes to |
|---|---|---|
| `main` | Stable | `seeds-release-latest` |
| `qa` | Promoted from develop, under test | `seeds-qa-latest` |
| `develop` | Integration — where work lands | `seeds-develop-latest` |
| `feature/<short-description>` | Your work | Nothing |

Branch off `develop`, merge back into `develop`. **Never commit directly to
`develop`, `qa` or `main`** — every push to those three publishes a channel, so a
direct commit is a release.

```bash
git checkout develop && git pull
git checkout -b feature/add-terraria-seed
```

Promotion is `develop` → `qa` → `main`, by merge, and carries every seed on the
branch. See [publishing.md](publishing.md).

## Commits

One logical change per commit, and one seed per commit where practical — a
commit touching three seeds is three things to revert separately later.

Write the message so it explains the decision, not the diff. The commit that
added Vintage Story is the model: it says why the seed downloads its own .NET
runtime, why configuration is a whole-file template rather than `manage: patch`,
and why the bundle is where it is. All three are things a reader would otherwise
have to re-derive.

Subject line in the imperative, under about 72 characters:

```
Add a Terraria seed
Fix Valheim's download URL after the 0.220 move
Bump Vintage Story to .NET 10
```

**Bump the seed's `version:` in the same commit as the behaviour change.** A
separate "bump versions" commit is how a change ships that nobody is offered.

## Before you open a pull request

```bash
ygg-seed validate seeds/<id>    # must pass — CI gates on it
ygg-seed lint seeds/<id>        # should be clean
```

Then the part neither command can do: **run it**. A seed that validates and has
never started a server is a hypothesis. See [testing.md](testing.md).

### Checklist

**Correctness**

- [ ] `ygg-seed validate` passes and `ygg-seed lint` is clean
- [ ] The directory name equals the seed's `id`
- [ ] `version:` is bumped, and higher than the published one
- [ ] `architectures` reflects what was actually confirmed, not what is assumed
- [ ] Every port's `protocol` was checked against real output
- [ ] Any `ready.pattern` was copied verbatim from output you have seen
- [ ] Any `crash.pattern` was watched firing more than once — or was left out
- [ ] `stop` shuts the game down cleanly, and the world survived a restart

**Branding** — required for every seed, not optional polish. See
[authoring.md](authoring.md#branding) for where to find these.

- [ ] `branding.icon` is set — never the top-level `icon:` emoji, which is a
      placeholder for a seed that has not been finished, not an
      alternative worth keeping once real art exists
- [ ] `branding.logo` and `branding.banner` are both set
- [ ] All three are real, on-topic art for this game or its dedicated-server
      tool — not a screenshot, not a generic placeholder
- [ ] Every image is one you may redistribute (an official CDN, press kit, or
      wiki mirror run by the developer — never a fan reupload of unclear
      origin)

**Compatibility** — for a change to an existing seed

- [ ] No variable or setting was renamed without `renamed_from`
- [ ] No option was removed from a `select` that operators may have stored
- [ ] A changed default is intentional, and noted in the PR
- [ ] Nothing in [conventions.md](conventions.md), "What counts as a breaking
      seed change", applies unsilenced

**Housekeeping**

- [ ] Comments explain the non-obvious decisions and say what was *not* verified
- [ ] No credential, personal file host, or link shortener in any URL
- [ ] No ADR numbers referenced from inside a seed

### What to put in the PR description

- What you ran it against — control plane version, node OS, container daemon.
- What you verified, concretely: installed, started, a client connected, stopped
  cleanly.
- **What you did not verify.** This is the most useful line in the description,
  and it belongs in a comment in the seed too, because the next person reads the
  seed and not the pull request.

## Review

A reviewer is checking three things, roughly in this order:

1. **Would this break an existing server?** Renames, removals, changed defaults,
   changed `manage`. This is the only category that destroys data, so it goes
   first.
2. **Was it actually run?** Against what, and what was skipped.
3. **Will the next person understand it?** Are the non-obvious values explained,
   and is the unverified part marked as unverified.

Style comes last and is not worth blocking on. A seed that works and reads oddly
is better than a tidy one nobody has started.

## Adding a seed to the embedded set

Deliberately, and as its own commit. The set embedded in the `yggd` binary lives
upstream at `seeds/library` and exists so a fresh install has seeds **with no
network at all** — it is an offline floor, not a mirror of this repository.

Promoting a seed there is a commit in the private repository, not a sync. There
is no wire-shape restriction on a newly authored seed: the compatibility test
upstream is scoped to seeds that *had* a schema 2 form and must keep installing
the way they always did, and a seed authored directly in schema 3 is compared
against nothing.

**Every seed in this repository is currently in both sets** — all five, and
byte-identical as of Vintage Story 2.0.0. So the paragraphs below are not a note
about one unusual bundle; they describe the normal case here, and you should
assume any seed you touch is embedded too until you have checked otherwise.

**Once a seed is in both, the two copies are independent and will drift — and
the drift has a direction that bites.** The catalog layer sits *above* the
bundled one, so an installed catalog bundle replaces the embedded copy entirely,
including when the embedded copy is newer. A fix that lands only upstream is
therefore invisible to every operator who installed that seed from the catalog.

So: **a seed change upstream must be pushed here too**, and with a version at
least as high. Check both before you assume a fix has shipped:

```bash
grep -m1 '^version:' seeds/<id>/seed.yaml                  # here
grep -m1 '^version:' ../yggdrasil/seeds/library/<id>/seed.yaml   # upstream
```

Fix a seed here first where you can — this is where it reaches operators.

## Keeping the mirrored docs current

[seed-spec.md](seed-spec.md) and [seed-fields.md](seed-fields.md) are **copies**
of files in the private control-plane repository, carried here because that
repository is private and this one is public. Do not edit them here — an edit
would be silently lost on the next refresh, and would be wrong in the meantime,
since the authority is the Go code upstream.

To refresh, from a checkout of both repositories side by side:

```bash
cp ../yggdrasil/docs/seed-spec.md   docs/seed-spec.md
cp ../yggdrasil/docs/seed-fields.md docs/seed-fields.md
```

Then **re-apply the two mirror headers** — the HTML comment and the paragraph
below the title in each — which the copy overwrites. Both explain that the file
is a mirror and that `internal/...`, `seeds/library`, `make seedschema` and every
ADR reference point at the upstream repository. Without them a reader here
follows a path that does not exist.

Commit the refresh on its own, with a message naming the upstream version it came
from.

**When to refresh:** whenever the format changes upstream — a new field, a new
install op, a changed rule — and at minimum whenever a `ygg-seed` release adds
something a seed here uses. A seed that validates against the tool while the
mirrored spec does not describe the field is the mirror being stale, not the seed
being wrong.

**How to tell it is stale:** `ygg-seed validate` accepts something
[seed-fields.md](seed-fields.md) does not list, or rejects something it does.

To fix something genuinely wrong in the *content*, fix it upstream and re-copy.
[seed-fields.md](seed-fields.md) is generated from the Go types, so it cannot be
hand-edited even there.

## The other docs

[architecture.md](architecture.md), [authoring.md](authoring.md),
[conventions.md](conventions.md), [publishing.md](publishing.md),
[testing.md](testing.md) and [decisions.md](decisions.md) belong to this
repository. Edit them here, in the same change as whatever they describe.

Record a decision in [decisions.md](decisions.md) when it is one a future reader
would otherwise re-litigate — why a seed is shaped an unusual way, why a
convention exists. Not for routine seed changes; a comment in the seed is the
right home for those.
