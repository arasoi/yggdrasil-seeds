# Testing a seed

> `ygg-seed validate` proves a seed **loads**. That is a much weaker claim than
> that the game runs, and the gap between the two is where every real seed bug
> has lived.
>
> This document is how to close it. Nothing here is automated — there is no test
> suite in this repository, because testing a seed means installing a game and
> starting it.

## What validation does and does not prove

| Validation catches | Validation cannot catch |
|---|---|
| A malformed document, a missing required field | A download URL that 404s |
| A template referencing an undeclared variable | A command the game rejects |
| A derived port naming a non-existent sibling | **A port declared TCP that is actually UDP** |
| A default a control would refuse | A readiness pattern the game never prints |
| A `rewrite` migration that is not idempotent | A config file the image overwrites at start |
| Every templated field failing to render | A stop command that corrupts the save |

Everything in the right-hand column is silent. A seed with the wrong protocol
starts cleanly, logs nothing wrong, and refuses every connection — and it will
validate, lint clean, pack, and publish.

## What you need

A real control plane, a real agent, and a real container daemon. In practice
that is a working Yggdrasil install with at least one node connected, plus enough
disk for the game.

The **mock fleet** upstream (`hack/mock-fleet.sh`) is **not** usable for this. It
runs the real agent stack over a fake runtime, so it never pulls an image, never
runs an install step, and never starts a game — and it strips readiness rules
outright, because there is no game to print a ready line. It is a UI fixture. It
will happily "run" a seed whose install is completely broken.

## Load the seed without publishing it

Point a control plane at a directory of seeds with `--seeds-dir` (or
`seeds_dir:` in `yggd.yaml`, or `YGG_SEEDS_DIR`):

```bash
yggd --seeds-dir /path/to/yggdrasil-seeds/seeds
```

That is the **operator** layer, which sits above both the bundled set and the
catalog — so a seed here overrides a published one with the same id, and you are
testing your working copy rather than whatever is installed.

Saving a seed through the control plane's own authoring UI triggers an in-process
reload. Editing a file on disk **does not** — restart `yggd` after an edit, or
you will be testing the previous version and drawing conclusions from it.

> Do not point `--seeds-dir` at a control plane whose data matters if you are
> also going to delete servers as you iterate. Use a scratch install.

## The pass

Work through these in order. Each one fails differently, and skipping ahead
means diagnosing several at once.

### 1. It loads

The seed appears under **New server → from a seed**. If it does not, `yggd`'s log
says which bundle it skipped and why: a bundle that will not load is skipped
rather than fatal, so a broken seed is silent in the UI and loud in the log.

### 2. The install actually installs

Create a server and watch the install job. This is where a wrong URL, a wrong
`strip_components`, or a SteamCMD app id with no Linux depot shows up — with real
progress and a real error rather than a guess.

Then check what landed on disk, on the node:

```
<installs_dir>/<install-id>/     # the files. Is the binary where the command expects it?
```

A `strip_components` off by one is the classic: everything unpacks one directory
deeper than the command looks, and the failure surfaces much later as a missing
file.

### 3. It starts, and the console proves it

Open the console. This is the single most valuable step, and the reason to do it
before writing a `ready` or `crash` pattern rather than after.

Read the output for real:

- **The line that means "up".** Copy it verbatim into `ready.pattern` — do not
  paraphrase it from memory or from a wiki. Check it is a regexp, not a
  substring: `Done (` needs escaping, and is exactly why Paper still has no
  pattern.
- **Whether it binds the port you declared**, and on which protocol.
- **Any fatal line** you might be tempted to use for `crash:`. Watch it happen
  more than once before you believe it.

### 4. A player can connect

The thing nothing else tests. Take the address the server's page shows and
actually join.

**Expect a non-conventional port.** Allocation scans the node's range, so the
game will not be on 25565 or 19132. If the client cannot be told a port, or the
image starts the server itself and never reads your command, this step is where
you discover the port has to be passed in explicitly.

### 5. Configuration lands, and survives a rebuild

Change a setting in the UI, save, and check the file on the node:

```
<servers_dir>/<server-id>/...
```

Two failures to look for specifically:

- **The value is not there.** The image owns that file and rewrote it at start —
  the setting needs an `env` destination instead of a `config.files` entry.
- **The value is there but the wrong type.** JSON `manage: patch` writes values
  as JSON strings, so a field the game expects as a number or boolean arrives
  quoted and the game rejects or ignores it. That needs a whole-file template.

Then save the settings form **again without changing anything**. A rebuild that
changed nothing must leave the file alone; if it does not, patching is not
idempotent and every rebuild is drifting.

### 6. It stops cleanly, and the world survives

Stop the server from the UI and watch the console. The stop command should
produce a clean shutdown well inside the timeout, not a `SIGTERM` escalation.

Then **start it again and confirm the world is still there**. A stop that
corrupts saves is the most expensive bug a seed can ship, and it is invisible
until the second start.

### 7. The second server on the same node

Worth doing once per seed, because a whole class of bug only appears here: the
first server usually gets tidy ports, and the second gets whatever is free. This
is where a hardcoded port, or a port published to the declared default rather
than the allocated one, surfaces.

If the seed has an `install` with `shared: true`, this also checks refcounting
and that the read-only mount plus writable overlays actually work.

## Extra passes for particular shapes

**A shared install** — create two servers off one install, confirm both start,
and confirm the install is not duplicated on disk. Check nothing writes into the
install directory: it is mounted read-only, and a game that expects to write
there needs a `writable_paths` entry.

**A cluster** — create two members, confirm both start independently, and confirm
the shared volume is mounted in both.

**`logs.values`** — restart the server and confirm the fact is re-extracted, and
that it disappears when the server stops. A stale join code is not merely old, it
is wrong.

**`logs.events`** — join and leave with a real client and watch the player count.

**A migration** — this needs a *before*. Create a server on the **published**
version of the seed, set the values you are about to migrate to non-defaults,
then switch to your working copy and rebuild. The operator's values must survive.
Doing it the other way round proves nothing, and this is the exact bug
`renamed_from` exists to prevent.

**An optional container (addon)** — create with it off, confirm no allocation is
held for it; enable it, confirm exactly its ports are added and nothing else
moves; disable it and confirm they are released.

## Before you publish

- [ ] `ygg-seed validate` and `ygg-seed lint` are clean
- [ ] The install completed against real infrastructure
- [ ] A client connected to a running server
- [ ] Configuration changes reached the game, and a no-op rebuild changed nothing
- [ ] It stopped cleanly and the world survived a restart
- [ ] A second server on the same node works
- [ ] Any `ready.pattern` was copied from output you have seen
- [ ] Any `crash.pattern` was watched firing more than once — or was left out

## Write down what you did not test

Put it in the seed as a comment, and in the PR. The existing bundles do this and
it is worth keeping up: Vintage Story records that only the linux-x64 tarballs
were confirmed and that no ARM64 server build was found, which is why it is
`architectures: [amd64]` rather than a guess. ARK records that its Steam subsystem
reports `FAILED` and that no real game client has confirmed it is harmless.

An honest "not verified" comment is worth more than silence, because the next
person reads the seed and not the pull request.
