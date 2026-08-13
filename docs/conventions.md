# Conventions

> House style for this repository. The format itself is in
> [seed-spec.md](seed-spec.md) — this is the part the validator will not tell
> you about.
>
> The five bundles here are the working examples. When something is not covered
> below, match what they do.

## Layout

```
seeds/<id>/
  seed.yaml                    the manifest
  configs/<name>.tmpl          config-file templates, if the seed renders any
  icon.png  logo.png  banner.png   branding, if it ships any
```

- **The directory name must equal the seed's `id`.** Nothing in the manifest
  enforces it, and `ygg-seed validate` on a whole directory checks it — because a
  mismatch loads fine on its own and then silently overrides, or loses to, a
  different seed once the layers merge.
- Bundles sit **directly under `seeds/`**. There is no `library/` here; that is
  the separate embedded set upstream (see [architecture.md](architecture.md)).
- Config templates go in `configs/` and are referenced by `source_path`, not
  pasted inline. Inline is for a one-line value where a separate file would be
  silly.
- Name a template after the file it produces, plus `.tmpl`:
  `configs/server.properties.tmpl`.
- **Never author `.ygg-source.json`.** The catalog writes it, and a bundle
  carrying one by hand claims a provenance it does not have.

## Naming

| Thing | Rule | Example |
|---|---|---|
| Seed `id` | kebab-case, and the directory name | `minecraft-java-paper` |
| Variable / setting names | identifier rules — lower_snake_case in practice | `world_name` |
| Log value names | same | `join_code` |
| `env` destinations | UPPER_SNAKE_CASE | `SERVER_NAME` |
| Container roles | short, lower-case, what it *is* | `game`, `postgres` |
| Port names | short, lower-case | `game`, `query`, `rcon` |
| Groups | Title Case — they are UI headings | `World modifiers` |

Two worth extra care:

**Name the primary container's port `game`** and mark it `kind: game`. Both are
how the UI finds the address to show an operator.

**Include the game in the id when the vendor's name is ambiguous.**
`minecraft-java-paper` says which Minecraft and which server implementation.

## YAML style

- Two-space indent. No tabs.
- Block style for anything with more than about three keys; **flow style for
  short, uniform rows** — a port, an option — where the alignment is the point:
  ```yaml
  ports:
    - { name: game,  protocol: udp, default: 2456, kind: game }
    - { name: query, protocol: udp, offset_from: game, offset: 1, kind: query }
  ```
- Quote anything that could be read as another type. Every `default:` is a
  string, so `default: "10"` and `default: "true"` — unquoted they are a number
  and a boolean, and the resulting error is about types rather than about the
  value you meant.
- `version:` is always quoted: `version: "2.2.0"`.
- Use `>-` for a description long enough to wrap.
- Emit keys in the canonical order the spec gives in §3. A stable order is what
  makes a seed written by a tool diff cleanly against one written by hand.
- Keep lines readable — roughly 100 columns for comments. Descriptions that a
  UI renders may run longer rather than being broken awkwardly.

## Comments

This is the convention that most distinguishes this repository, and it is worth
keeping up. The seeds here are heavily commented, and the comments carry a
specific kind of information: **why a value is what it is, and what was actually
verified.**

Comment when:

- **A value is non-obvious or was hard-won.** Why Vintage Story downloads its own
  .NET runtime instead of using `base-dotnet`; why ARK needs a particular Proton
  environment variable.
- **A rule belongs to the game rather than to the seed.** Valheim's password
  constraints are enforced by the game at startup, and the seed says so rather
  than inventing a second place to keep in sync with Iron Gate.
- **Something was deliberately not done.** Why a seed is `architectures: [amd64]`
  rather than guessing at an ARM64 URL that may not resolve. Why a `crash:` rule
  is a comment and not a field.
- **A candidate pattern is unverified.** Keep it as a comment with a note that it
  has not been seen in real output. That is exactly why Paper and Bedrock still
  have no `ready.pattern`.

Do not comment what the field already says. `# the server name` above
`name: server_name` is noise.

**Do not reference ADR numbers in a seed.** Those live in the private
control-plane repository and a reader here cannot follow them. Say the reasoning
instead — this repository's own [decisions.md](decisions.md) is the exception,
since that is where cross-repository context belongs.

## Descriptions are UI text

`label` and `description` are rendered on a form an operator reads while deciding
what to set. Write them for that reader:

- A `label` is a short noun phrase in sentence case: `Max players`, not
  `MAX_PLAYERS` or `The maximum number of players`.
- A `description` says what the setting *does* and what happens at the extremes,
  in one or two sentences. Bedrock's `online_mode` says plainly that turning it
  off means anyone can join as anyone — that is what an operator needs at the
  moment they are looking at the toggle.
- Say the consequence, not the mechanism. "Off lets unauthenticated clients join"
  beats "sets `online-mode=false`".
- Use `group` to keep a large surface navigable, and `show_if` to hide a control
  that is meaningless until another is on — an RCON password with RCON off.

## Versioning

Every seed carries its own `version:`, `MAJOR.MINOR.PATCH`, independent of
Yggdrasil's.

- **Bump it whenever behaviour changes.** Nothing enforces this. The packer can
  only reject a version it cannot *order*, not one that is merely stale, and
  forgetting means nobody is ever offered your change.
- **Patch** — a fixed URL, a corrected description, a comment.
- **Minor** — a new variable or setting, a new optional container, a new
  readiness rule.
- **Major** — a breaking seed change. See below.
- **Never decrease it.** A control plane orders versions and reads a lower one as
  "older" rather than offering a downgrade, so an operator on the bad version is
  stuck. Always fix forward.
- A comment-only change may skip the bump. If in doubt, bump the patch.

## What counts as a breaking seed change

Anything that changes behaviour for a server that **already exists**. These are
the ones that cost operators real data, so they get named:

| Change | Why it bites |
|---|---|
| Renaming a variable or setting | Stored values are keyed by name, so the operator's value is discarded and the default reinstated — **silently** |
| Removing one | The same, with nothing to carry the value to |
| Changing a default | Only affects servers that never set it — but those are exactly the servers nobody is watching |
| Narrowing a `select`'s options | A stored value that is no longer offered |
| Changing `manage` on a config file | `always` starts discarding hand edits; `once` starts ignoring your template |
| Changing a port's protocol or its `offset_from` | Reallocation, and possibly a server nobody can reach |

**Renaming is only safe with `renamed_from`:**

```yaml
- name: crossplay
  renamed_from: [crossplay_flag]
```

That desugars into a rename migration, so a value stored under the old name is
carried forward once, idempotently. Without it, renaming Valheim's
`crossplay_flag` would have turned crossplay back **on** for every server where
an operator had turned it off.

Migrations record nothing per server, which is affordable only because each is
idempotent by construction — a `rewrite` map whose values intersect its keys is
rejected at load. Do not try to be clever here; the validator is the guarantee.

## Ports

- `protocol` is required, and **check it against real output**. A UDP game whose
  seed says `tcp` starts cleanly and refuses every connection.
- `default` documents the game's conventional port. It is **not** an allocation
  preference — a node's configured range is the whole candidate pool.
- Use `offset_from` only for a relationship the game hardcodes and gives you no
  flag to change. Ports that merely happen to be adjacent are two independent
  ports.
- Give every port a `kind` when it is not the main one, so administrative ports
  stay out of an operator's way.

## Install steps

- Prefer a maintained third-party image with no install at all. Less to go wrong.
- Use `shared: true` only when servers genuinely should share one copy of the
  files. Two worlds of the same game usually should not.
- A shared install may not reference per-server data — the validator enforces it,
  but design for it rather than discovering it.
- **Pin what you can.** A URL templated on a version variable is better than a
  "latest" redirect, because an operator can pick a version and reproduce it.
- **A download URL runs on somebody else's node.** Publishing a seed asks every
  operator who installs it to fetch that URL and run what comes back. Use the
  vendor's own host, prefer HTTPS (the validator does not require it — you
  should), and do not point an install at a personal file host or a link
  shortener.
- Say in a comment which platform and architecture a URL was confirmed against.

## Readiness, stop, crash

- **Only write a `ready.pattern` you have seen in real output.** It is a regexp,
  not a substring — `Done (` needs escaping.
- `mode: port` is the right first choice for a game added blind: it needs no
  game-specific knowledge.
- Get `stop` right before publishing. Most game servers want a console command,
  and losing that distinction corrupts world saves.
- **Prefer no `crash:` rule to an unverified one.** A wrong readiness pattern
  delays a server; a wrong crash pattern stops a healthy one. `ygg-seed lint`
  warns about any crash rule at all.
- Keep an unverified candidate as a comment, with a note saying it is unverified.

## Branding

- Slots are `icon`, `logo` and `banner`, naming files inside the bundle.
- Ship images you have the right to redistribute — a published bundle is served
  from **other operators'** control planes, not yours.
- Prefer a raster (`.png`, `.jpg`, `.webp`). An SVG is a document that can carry
  script; hand-placing one is a decision about your own control plane, and
  shipping one in a published bundle makes it everybody's.
- `branding.accent` is reserved and applied by nothing. Setting it changes
  nothing.
- Never copy a `branding:` block into a new seed without replacing the files —
  the filenames resolve against the new seed's id and will 404.

## Secrets

Never put a real credential in a seed. A seed is published to a public
repository and downloaded by strangers.

Use `generate: password` for anything that must be secret per server — Paper's
RCON password is the case it exists for, and an empty one makes the server refuse
to start. Use `type: password` so the UI treats it accordingly. A placeholder
default like `changeme123` is acceptable where the game requires a non-empty
value, but say so in the description.
