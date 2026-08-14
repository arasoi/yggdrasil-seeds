# The seed format

<!--
  MIRRORED FILE — do not edit here.

  The upstream copy lives in the Yggdrasil control-plane repository at
  docs/seed-spec.md, next to the `internal/seed` package that defines the
  format. This is a verbatim copy, carried here because that repository is
  private and this one is public: a seed author needs the format, and a link
  they cannot open is not a specification.

  Fix anything wrong with this document upstream and re-copy. See
  contributing.md, "Keeping the mirrored docs current", for the procedure and
  for how to tell whether this copy has fallen behind.

  Paths like `internal/seed`, `seeds/library` and `make seedschema`, and every
  ADR-NNN reference, are to that upstream repository. Nothing in this
  repository has a Go package or a Makefile. §16 in particular describes both
  repositories: this one is the publisher, and `seeds/library` upstream is the
  separate embedded set.
-->

> **Schema version 3.** A seed is a game definition: everything Yggdrasil needs to
> install a game, run it, configure it, and know when it is up.
>
> This document explains the format. [seed-fields.md](seed-fields.md) is the
> generated field list, and `internal/seed/schema.json` is the machine-readable
> schema. See ADR-077 for why the format is shaped this way.
>
> **This is a mirror.** The authority is `internal/seed.Validate` in the
> control-plane repository, and the practical test of any claim here is
> `ygg-seed validate`, which calls exactly that code. Where this document and
> the tool disagree, the tool is right.

## 1. About this document

### 1.1 What is normative

**`internal/seed.Validate` is the definition of the format.** Not this document,
and not the JSON Schema.

That is not modesty about the prose. It is because the rules that matter most are
cross-field, and no schema language expresses them: exactly one container is
primary, a derived port must name a sibling that is not itself derived, a
variable's default must satisfy that variable's own control rules, and every
templated string must dry-render against the seed's own declarations. Those live
in Go and nowhere else.

Everything else is generated from those types:

| Artifact | What it is | Kept honest by |
|---|---|---|
| `internal/seed/schema.json` | JSON Schema 2020-12, for editors and external tools | A test that fails if the committed file differs from freshly generated output |
| [seed-fields.md](seed-fields.md) | Every field, with its type and tier | Generated in the same pass |
| This document | Prose: what the fields mean and why | Nothing. Read it as explanation, not as authority |

`make seedschema` regenerates the first two. If this document and the validator
disagree, the validator is right and this document has a bug.

### 1.2 Tiers

Every field declares how much you may rely on it. The tier lives in a struct tag
on the Go field and travels into the schema as `x-ygg-tier`, so it is stated once
rather than in three places that could disagree.

| Tier | Means |
|---|---|
| `stable` | Has a consumer. Will not change shape without a schema version bump. |
| `provisional` | Has a consumer. Its shape may still change within schema 3. |
| `reserved` | **Specified and validated, with no consumer.** Setting it changes nothing. |

Reserved deserves the emphasis. Schema 2 had `logs.ready`, a field all four
bundled seeds set and nothing ever read — for months, with no way for an author to
tell (ADR-067). Marking a field reserved is how this format says "written down so
your document keeps loading when the consumer lands, but it does nothing today".

### 1.3 Where a rule is enforced

- **Load time** — `Validate`, when a seed is read. A seed that fails does not
  load. This is where almost everything is.
- **Provision time** — when a server is built. Only for things that depend on the
  control plane's own state, such as resolving a symbolic base image.
- **Lint** — warnings that must not block loading. See §11.

---

## 2. Bundle layout

A seed is a directory, not a file.

```
<seed-id>/
  seed.yaml            # the manifest. seed.yml also accepted
  configs/             # config-file templates, referenced by source_path
    server.properties.tmpl
  icon.png             # referenced by branding.icon
  .ygg-source.json     # written by the catalog. Never author this
```

Rules:

- The manifest is `seed.yaml` or `seed.yml`. Nothing else is required.
- Every path a seed names — `source_path`, `branding.icon`, a `bundle:` install
  source — is **relative to the bundle root**, may not start with `/`, and may not
  contain `..`.
- A directory whose name starts with `.` is skipped, which is why the provenance
  marker is inert.
- Files the manifest does not reference are ignored, not rejected.

### 2.1 The three layers

Seeds load from three places, later winning entirely over earlier:

| Layer | Where | Why it is at this level |
|---|---|---|
| bundled | embedded in the `yggd` binary | a fresh install has seeds with no network at all |
| catalog | `<data_dir>/seeds/<id>/` | downloaded, updated on its own schedule |
| operator | `<seeds-dir>/<id>/` | hand-authored, so a catalog update can never overwrite it |

Merging is by `id`, whole-seed: two seeds sharing an id are the same seed, and the
higher layer replaces the lower one completely. There is no field-level merge.

**A bundle that will not load is skipped, not fatal.** The catalog and operator
layers hold files the running binary did not ship, so tightening a validation rule
can invalidate a bundle that was fine when it was installed. Refusing to start
then crash-loops the control plane over a file it could ignore, with no UI left to
remove it (ADR-076's amendment). Only the embedded set is strict — a failure there
is a build defect.

---

## 3. The document

Top-level keys, in the order a tool must emit them:

```
schema  id  name  version  description  icon  branding  architectures
install  server  cluster  containers
variables  groups  settings  config
ready  crash  stop  logs  connect  backup  migrations
```

A stable order is what makes a seed written by a tool diff cleanly against one
written by hand. The order is recorded in the schema as `x-ygg-order`.

### 3.1 Identity

```yaml
id: minecraft-java-paper
schema: 3
name: Minecraft (Java, Paper)
version: "2.2.0"
description: Paper server for Minecraft Java Edition.
icon: "⛏️"
architectures: [amd64, arm64]
```

- **`id`** is kebab-case and is the merge key. Changing it creates a different
  seed.
- **`schema`** must be `3`. A schema 2 document is up-converted on load (§12), so
  it still works — but a tool should emit 3.
- **`version`** is the *seed document's* revision, not the game's. It must be
  `MAJOR.MINOR.PATCH`: `version.Compare` cannot order anything else, and a version
  nothing can order is a seed nobody can ever be told to update. **Bump it
  whenever behaviour changes.** Nothing enforces that — the packer can only reject
  a version it cannot *order*, not one that is merely stale.
- **`architectures`** is empty for "no restriction". Declaring it is how a
  mismatch becomes a clear refusal at creation time instead of an opaque
  exec-format crash-loop (ADR-016).

---

## 4. Images

```yaml
image: "itzg/minecraft-bedrock-server"          # verbatim, never rewritten
image: { ref: "eclipse-temurin:21-jre-alpine" } # the same thing, canonically
image: { base: steamcmd-proton }                # this project's own library
image: { base: steamcmd, channel: develop }     # pinned to a channel
```

A bare string is accepted and normalised to `{ref: ...}`. The mapping is
canonical, and a tool should emit it — a document that flips between the two forms
depending on which fields happen to be set is a document that churns in git.

**`base` names one of this project's published base images** (`linux`,
`steamcmd`, `steamcmd-proton`, `java`, `dotnet`) and is resolved to a registry
reference at provision time. It exists because a seed writing
`ghcr.io/arasoi/base-linux:release-latest` hardcodes both an owner and a channel,
and ADR-073 records a real library fix that could not reach a node for exactly
that reason: `release-latest` is built only from `main`, so a fix on `develop` was
unreachable until it was promoted. With `base`, a `develop` control plane pulls
`develop` images without every seed having to say so.

An unknown `base` is a **warning at load and an error at provision**, never a load
failure. Adding an image to the library would otherwise mean an older binary
rejects a newer seed, and rejection at load makes the seed vanish from the picker
with nothing explaining why.

Each base carries a descriptor at `images/<name>/base.yaml`, embedded in the
binary, recording what it provides, which architectures it is published for, how it
runs, and which environment variables it honours. The **registry name comes from
that descriptor**, not from assembling `"base-" + name`, so a base whose directory
and seed-facing name diverge still resolves to something that exists. Only the
descriptors are embedded — a Dockerfile stays data a human or CI builds.

Use `ref` for any third-party image. That is the majority case and always will be.

---

## 5. Install

```yaml
install:
  shared: false
  mount: { path: /game, mode: ro }
  image: { base: steamcmd }     # only when a step needs a container
  steps:
    - op: steamcmd
      app_id: 896660
```

`install` is absent when the container image already contains the game — Minecraft
Bedrock's image downloads the server itself at start, so it has no install at all.

- **`shared: true`** materialises the files once and mounts them read-only into
  every server that references them, refcounted (ADR-018). Five ARK maps, one
  50 GB install.
- **`mount.mode`** defaults to `ro`, which is what the writable-overlay model
  requires. Paths the game must write to are bind-mounted over the top from the
  server's own directory.

### 5.1 Steps

Schema 2 had `method: download|steamcmd` plus five conditionally-required
siblings. It could express exactly two installs. A game needing
fetch-then-extract-then-chmod had no expression at all, and the obvious
alternative — an install shell script, which is what most panels do — would make a
seed *code*, which ADR-007 rules out and which no form can generate.

So an install is an ordered list of typed operations, discriminated by `op`:

| `op` | Tier | Does |
|---|---|---|
| `download` | stable | Fetches `url` to `into` |
| `extract` | stable | Unpacks `from`, optionally `strip_components` |
| `steamcmd` | stable | Installs `app_id`. **Needs a container** |
| `mkdir` | provisional | Creates `path` |
| `copy` | provisional | Copies `from` to `to`, optionally only `if_missing` |
| `move` | provisional | Renames `from` to `to` |
| `chmod` | provisional | Sets `mode` (octal, quoted) on `path` |
| `write` | provisional | Writes templated `content` to `path` |
| `patch` | provisional | Sets `set` keys in `path`, by `parser` |
| `start_app` | **reserved** | Boots the game so it writes its own config |
| `wait_ready` | **reserved** | Waits for a started app |
| `stop_app` | **reserved** | Shuts down a started app |

Every step accepts `name` (a label for progress output) and `if` (a condition on a
variable — settings do not exist at install time).

Three rules worth knowing before you write one:

1. **A field belonging to a different op is rejected, not ignored.** The step is a
   flat object, so every field parses on every op. Writing `from:` where `into:`
   belongs would otherwise give you a step that silently does nothing.
2. **`install.image` is required exactly when a step needs a container, and
   forbidden otherwise.** A plain download runs in the agent process with no image
   pull at all; declaring an image it will never use would read as though it did
   something.
3. **A shared install may not reference per-server data** — no `.ServerID`,
   `.ClusterID`, `.Ports`, `.Settings` or `.Endpoint` in any step. The directory is
   mounted read-only by every server referencing it, so baking one server's value
   into it is silently wrong for all the others. (Schema 2 had this hole open.)

`download`'s `into` is required, where schema 2 let it default to the URL's
basename. That default was a trap: a templated URL's basename depends on a
variable, so the path a container command references could change underneath it.

**`extract` removes the archive after unpacking it.** An archive that has been
unpacked into the same install has no further purpose, and leaving it doubles the
install's disk footprint — which for a multi-gigabyte download is not a rounding
error. `strip_components` drops leading path elements for the very common archive
that wraps everything in one version-named directory; an archive that does not
wrap its contents that deeply is an error rather than a guess, since guessing
would silently drop files.

Two things are declared and **not yet performed by the agent**:

- **`copy` from `bundle:<path>`.** The agent has no access to a seed bundle at
  all — it never parses seed YAML (ADR-012) — so this would require the control
  plane to send the file's bytes, which is its own decision about whether a seed
  may ship payloads into an install. It fails with a message naming the reason
  rather than being skipped.
- **`patch` with `parser: xml`.** See §8.

Both fail loudly. An install step that was silently skipped would produce an
install missing files and report success, and that install is then mounted
read-only into every server referencing it and fails obscurely at start.

### 5.2 What the server owns

```yaml
server:
  writable_paths:
    - { from: saved,  to: /game/ShooterGame/Saved }
    - { from: config, to: /game/ShooterGame/Saved/Config }
  file_denylist:
    - "configs/*"
```

`writable_paths` bind-mount the server's own directories over the read-only
install, which is how a shared install works at all (ADR-018).

`file_denylist` names glob patterns under that writable root that file operations
refuse to list, read, write, delete or rename. It is for the files the **seed
itself** regenerates: without it the browser invites an edit the next rebuild
silently discards, which is worse than not offering the edit.

**Not a security boundary.** The sandbox is — containment against the real,
symlink-resolved root is what stops a path escaping, and that is unchanged and
unconditional. This is about not inviting a pointless edit, so its worst failure is
a confusing refusal rather than an exposed file. It is nonetheless enforced on the
agent as well as hidden in the UI, because a node must not depend on the thing
sending it commands being correct.

Patterns are read literally, and `*` does not cross a separator: `configs/*` names
the files in that directory, and `configs` names the directory *and everything under
it*. Inferring the second from the first would leave no way to say the first. A
denied entry is omitted from a listing rather than shown and then refused, and the
root itself is never denied — a pattern that hid it would leave the browser with
nothing to show and no way to say why.

---

## 6. Containers

Every server is a pod, even with one container (ADR-017). Exactly one container is
`primary`.

```yaml
containers:
  - role: game
    primary: true
    image: { base: linux }
    command: "./server -port {{.Ports.game}}"
    workdir: /game
    env:
      SERVER_PORT: "{{.Ports.game}}"
    ports:
      - { name: game,  protocol: udp, default: 2456, kind: game }
      - { name: query, protocol: udp, offset_from: game, offset: 1, kind: query }
```

- **`role`** names the container within the pod. The primary's role is rewritten to
  `primary` on the wire whatever the seed calls it, because console attach and
  allocation lookups have no way to find a differently-named one. Anything
  referring to a container by role resolves through that same rewrite.
- **`command`** is templated, then split with POSIX-ish quoting. It is **not run
  through a shell**: no expansion, no globbing, no pipes. Write `sh -c '...'`
  explicitly if you need those.
- **`optional: true`** makes a container an addon: shipped with the seed,
  provisioned only if the operator enables it. A map renderer or a database admin
  UI. An optional container cannot be primary, nothing non-optional may depend on
  one, and **no template may reference an optional container's port** — it has no
  allocation when the addon is off, and a missing key fails the render.

  A disabled addon holds **no allocation**, and enabling one allocates only its own
  ports without moving any the server already holds. Ports are released when it is
  disabled, on the next rebuild rather than at the moment of the save, so the
  invariant "an allocation exists exactly when something publishes it" is
  re-established on every rebuild rather than depending on one having succeeded. A
  role the seed no longer declares at all is left alone: that is what a *renamed*
  container leaves behind, and dropping a port a running server may still be
  serving on is the worse outcome.

  `name` and `description` are what the operator reads when choosing; a seed that
  gives neither shows the role.

### 6.1 Ports

- **`protocol`** must be `tcp` or `udp`. Empty is rejected rather than defaulted,
  because a game whose port is UDP and whose seed forgot to say so starts cleanly,
  logs nothing wrong, and refuses every connection (ADR-061).
- **`default` is not an allocation preference.** Allocation scans the node's
  configured port range and nothing else, because a range an operator set is their
  statement of which ports actually work on that host. This field documents the
  game's conventional port and supplies the authoring form's preview value. It is
  required unless the port is derived.
- **`offset_from` / `offset`** derive a port from a sibling on the same container,
  for a game that hardcodes the relationship — Valheim's Steam query port is always
  `game_port + 1` with no flag to set it separately. No chaining.
- **`kind`** says what the port is *for* (`game`, `query`, `rcon`, `web`, `voice`,
  `other`), so the UI can show players the number that matters and keep an
  administrative one out of the way. At most one `game` per seed.

Host and container port are always the same number: the game binds what it was
told to bind, so that is what it must be published to.

---

## 7. Variables and settings

Two blocks, and the distinction is a real one:

> A **variable** shapes how the server is *built* — it reaches a command, an env
> value, an install step, a mount. Changing one requires the pod to be rebuilt.
>
> A **setting** is written into the game's own configuration, and says where. It
> needs no template line.

If you are unsure: does the value reach a command line or an install? Variable.
Does it reach a config file or an env var that only the game reads? Setting.

Both share one `Control` type, so both render with the same form components and
obey the same validation. Names live in **one namespace** — declaring the same
name in both blocks is a load error rather than a shadowing surprise.

### 7.1 Controls

```yaml
- name: difficulty
  type: select
  label: Difficulty
  description: How hard the world is.
  group: World
  default: normal
  editable: true
  options:
    - { value: peaceful, label: Peaceful }
    - { value: normal,   label: Normal }
    - { value: hard,     label: Hard }
```

A value is **always a string**, whatever `type` says. The type governs how the
value is chosen and checked, never how it renders — so a seed keeps full control
of the emitted text. A bool's `true_value` can be a whole flag (`-crossplay`), and
a select's value can be a bare word the command wraps in its own `{{if}}`.

Types: `text` (the default), `password`, `number`, `range`, `select`, `radio`,
`bool`.

Three rules that bite:

1. **`min`, `max` and `step` are the browser's rules too.** HTML's step *base* is
   `min` whenever one is set, not zero — so `min: -1, step: 1000` makes every round
   number a step mismatch. A control that fails constraint validation inside a
   collapsed group or behind a `show_if` cannot be focused, so the browser refuses
   the whole submit **silently**. A default that misses the grid therefore fails at
   load (ADR-076's amendment).
2. **`required` cannot be combined with `show_if`**, for the same reason: an empty
   required field behind a false condition blocks the form with nothing on screen
   to explain it.
3. **A default must be a value the control accepts.** A default the form would
   offer and then refuse is the sharpest possible contradiction.

`generate: password|uuid|hex` fills the value per server, so a secret is never
typed into a form or left blank. Paper's RCON password is the case it exists for —
an empty one makes the server refuse to start, which is exactly how it happens by
accident.

### 7.2 Conditional visibility

```yaml
show_if: { name: enable_rcon, equals: "true" }
show_if: { name: resource_pack, not_equals: "" }
```

One comparison against one other variable or setting. Not an expression tree — a
condition language grows teeth quickly, and one comparison has covered every case
the bundled seeds produce.

**A hidden control still submits its value.** Visibility is presentation only, so
nothing server-side has to mirror the rule, and a setting an operator once
configured is not silently dropped because they later switched off the thing that
revealed it.

`groups:` optionally decorates a group with a description or a collapsed default.
It does **not** define membership or order: those come from the declarations
themselves, so the two can never disagree about what groups exist.

### 7.3 Destinations

A setting says where its value lands. Exactly one of:

```yaml
to: { file: server.properties, key: max-players }
to: { env: SERVER_NAME }
to: { env: LEVEL_NAME, container: game }
to: { file: server.properties, key: rcon.password, if: { name: enable_rcon, equals: "true" } }
```

- **`file` + `key`** must name a `config.files` entry managed `patch`.
- **`env`** targets a container's environment. A container may not declare an
  `env:` key a setting also targets — that would be two writers and a precedence
  rule nobody would remember, so it is a load error.
- **`if`** writes the destination only when the condition holds. This is what makes
  a guard like "only enable RCON when a password is set" declarative rather than a
  template conditional.

### 7.4 The tri-state

Settings distinguish three states, which is what a game whose own image rewrites
its config file needs:

| State | Spelled | Means |
|---|---|---|
| absent | not stored, and `optional: true` | **Leave the destination alone.** Do not write the key; do not set the env var |
| empty | `""` | Write it, empty |
| set | anything else | Write it |

`optional: true` is what permits absence. Schema 2 could not express this at all —
every declared variable always rendered into its env line.

**What absence protects, and what it does not.** A settings form renders every
control, so **saving it makes every optional setting present**. Absence therefore
covers the case that matters — a seed gaining a setting does not start writing it to
servers that already exist — but it does not survive an operator pressing Save.
Leaving one deliberately unset needs a per-control affordance the form does not have
yet.

---

## 8. Config files

A file is either **generated whole** from a template, or **patched by key**.

```yaml
config:
  files:
    - path: eula.txt
      source_path: configs/eula.txt.tmpl
      manage: once

    - path: server.properties
      parser: properties
      manage: patch
      set: { "server-port": "{{.Ports.game}}" }
```

| `manage` | Does | Use for |
|---|---|---|
| `always` | Rewrites the whole file from the template on **every rebuild** | A file the seed owns outright. The default for a templated file, and schema 2's only behaviour |
| `once` | Writes it only if absent, so operator edits survive | A first-boot gate that depends on nothing — `eula.txt` |
| `patch` | Sets only the named keys, preserving comments, ordering, and everything else | A file the game itself owns and rewrites |

`patch` is read-modify-write against the file on the node, and it is the only thing
on the provisioning path that **reads**. A read that fails, or comes back truncated,
degrades to writing the declared keys alone rather than failing the rebuild — a node
under load must not make a server unprovisionable. A truncated read is never merged
into, since writing that back would silently delete whatever the read did not reach.

Two costs worth stating plainly, because neither is obvious:

- **`manage: always` discards an operator's hand edits on every rebuild.** That was
  true before this field existed too; now at least the seed says so.
- **`manage: once` fails silently forever.** A later change to the template never
  reaches a server that already has the file, and nothing about that server
  indicates it.

Template text comes from `template` (inline) or `source_path` (a file in the
bundle) — never both. `source_path` is resolved into `template` at load, so
everything downstream sees only `template`.

Parsers and their key syntax:

| `parser` | Key syntax | Notes |
|---|---|---|
| `properties` | `key` | Line-oriented: comments, ordering and CRLF all survive. A key the file lacks is appended; a *commented-out* one is left as a comment and a new assignment added, since uncommenting a documented default would change behaviour nobody asked for |
| `ini` | `Section/Key`, `/Key` for the file's head | Split on the **last** slash, because an Unreal section name is itself slash-separated (`/Script/Engine.GameSession`). A new key lands inside its own section, never at the end of the file, where it would be read as belonging to whichever section precedes it |
| `yaml` | `a.b.c` | Edited as a node tree, so comments and key order survive. A scalar's type is re-inferred from the text on the way out, which is what a game's parser wants |
| `json` | `a.b.c` | **Normalised**: Go maps have no order, so a patched file comes back with keys alphabetical and a two-space indent. Same content, different shape |
| `xml` | — | **Not implemented.** Declared so the format need not change to gain it later, and refused with a message naming it |

Patching is idempotent: applying the same set of keys twice produces the same
bytes, which matters because `manage: patch` runs on every rebuild and a rebuild
that changed nothing must leave the file alone.

### 8.1 Importing what is already on disk

```yaml
- path: server.properties
  parser: properties
  manage: patch
  importable: true
```

`importable` lets an operator read this file back off the node and adopt the values
the seed recognises onto that server's stored settings. It is the migration path
for a server somebody else configured by hand, or a file edited through the browser
before the seed had a setting for that key — otherwise the next rebuild overwrites
it silently.

Set it only on a file the **game or an operator** writes. On a file the seed
generates wholesale it would re-read what the seed just wrote, and on one the game
rewrites in a shape the parser does not round-trip it would adopt nonsense. The
seed is the only thing that knows which of its files an operator's edits are worth
keeping.

Only values that actually differ are adopted, and a file that could not be read
whole contributes nothing — adopting part of it would leave some keys agreeing and
others silently not, which is the same judgement patching makes in the other
direction.

---

## 9. Lifecycle

### 9.1 Readiness

```yaml
ready:
  mode: log
  pattern: "Game server connected"
  timeout: 120s
  on_timeout: warn
```

| `mode` | Waits for |
|---|---|
| `immediate` | Nothing. **The default**, and bit-for-bit what every seed did before this existed |
| `log` | `pattern` (a Go regexp) in the primary container's output |
| `port` | The named allocated port to accept a connection |
| `healthcheck` | The primary container's own healthcheck |

Declaring a *mode* rather than just a pattern is what makes log-based readiness
safe to adopt. Schema 2 had `logs.ready`, a bare substring that four seeds declared
and nothing matched, because making readiness depend on a match risked stranding a
healthy server in `starting` forever when a pattern was wrong (ADR-067).

Two things prevent that now: `immediate` is the default, so opting in is
deliberate; and `on_timeout: warn` — also the default — reports the server
**running** with a stated reason rather than leaving it in limbo. A wrong pattern
delays a server; it does not strand one. Same judgement ADR-031 makes about
adoption: prefer the recoverable failure.

`mode: port` needs no game-specific knowledge at all, which makes it the right
first choice for a game you are adding blind.

A pattern on a mode that does not use one is **rejected**, not ignored. A field
that looks like it does something and does not is the whole problem this replaced.

**Where the reason goes.** A timed-out wait reports the server running *with a
reason*, shown on the fleet list and on the server's own page. That is the only sign
anything was odd, so it is never empty — "running" with no explanation is worse than
the `starting` limbo it replaces, because at least limbo is visibly wrong.

**A sidecar restart does not re-wait.** Bringing one crashed sidecar back never
touched the primary, so the pod already satisfied its readiness rule and the
evidence has scrolled past — a line printed at startup is not reprinted because a
database came back. Only the paths that restart the primary re-establish readiness.

**Write a pattern only if you have seen it in real output.** ARK's and Valheim's
are verified live and are fields; Paper's and Bedrock's are not, so those seeds
stay `immediate` and keep their candidates as comments.

### 9.2 Stop

```yaml
stop:
  command: "stop"
  timeout: 60s
  then: SIGTERM
```

Most game servers want a console command rather than a signal, and losing that
distinction corrupts world saves. The command goes to the primary's stdin; after
`timeout`, `then` is sent.

### 9.3 Crash

```yaml
crash:
  mode: log
  pattern: "Fatal error"
```

`mode: none` is the default: a crash is a container exit and nothing else, which
is all it ever was. `mode: log` also treats `pattern` appearing in the primary's
output as a crash, **before the process itself exits**.

That case is real rather than hypothetical — ADR-047 records ARK hanging
indefinitely inside Crashpad's startup with the process alive and nothing ever
exiting, which exit-code detection cannot see and no restart policy can help.

**A match kills the pod.** Marking a server crashed while its containers keep
running would be a state the machine cannot act on: the restart policy fires on an
exit, and there would not be one. So the verdict is carried out and the ordinary
exit path does the transition and the restart, with the matched line recorded as
the reason rather than "killed".

**Only write a pattern you have seen behave.** The bar here is higher than
readiness's, and by more than it looks: a wrong readiness pattern *delays* a
server, a wrong crash pattern *stops a healthy one*. Neither bundled seed that once
declared a candidate here still does — both are comments, because neither was ever
checked against real output. `ygg-seed lint` warns about any crash rule for the
same reason.

A line printed while a server is being stopped is not a crash, and neither is one
matched on a pod that is already going down: the state is checked before the line
is acted on. The first matching line wins, so a game printing its fatal error a
dozen times while it unwinds produces one kill.

---

## 10. Logs

```yaml
logs:
  values:
    - { name: join_code, label: "Join code", fleet: true, pattern: "join code ([0-9]+)" }
  events:
    - { event: join,  pattern: "(?P<player>\\S+) joined the game" }
    - { event: leave, pattern: "(?P<player>\\S+) left the game" }
```

**`values`** extract a named fact a player needs that only the running server
knows. Valheim's six-digit join code is the case it exists for: it changes on every
restart and appears nowhere but the log. The pattern needs **exactly one** capture
group — with several there is no obvious answer to which is the value, and silently
taking the first would make an author's mistake look like a feature. `fleet: true`
puts the fact on the servers list, so the seed decides what is worth seeing at a
glance rather than the UI hardcoding it.

Facts are discarded when a server stops: a join code from a previous run is not
stale but *wrong*.

**`events`** recognise well-known occurrences from a fixed vocabulary, using
**named** capture groups. `join` and `leave` need `player`; `chat` needs `player`
and `message`; `update_available` needs `version`. A named group the event does not
define is rejected rather than ignored — a typo'd group name would otherwise
produce an event with an empty field and nothing explaining why. `chat` and
`update_available` are **reserved**.

`join` and `leave` maintain that server's player list, shown on its page and as a
count on the fleet list. It is observed state and nothing more: derived from what
the game printed, cleared when the server stops (who was online during the previous
run is not stale information, it is wrong), and depended on by nothing — which is
what makes a dropped event cosmetic rather than a correctness problem.

Two asymmetries worth knowing. A join is idempotent and keeps its original
timestamp, so a game that reprints its player list on a timer does not restart
everybody's clock; and a leave for somebody not listed is a no-op, because the join
may have been dropped and the honest outcome of that is the same absence either way.

The count is shown **only for a seed that declares one of these rules**. "0 players"
on a server nobody is counting is a confident wrong answer where saying nothing is a
missing one.

A pattern runs against every line the primary prints, so keep it anchored and
cheap.

---

## 11. Validation, and what is deliberately not validated

`Validate` is strict about anything it can check without touching the filesystem
or the network. Two rules are deliberately **lint-only**, because Validate is a
compatibility surface — every rule is applied to bundles an *older* release wrote,
sitting on an operator's disk:

| Rule | Why it is lint, not load-time |
|---|---|
| `version` parses as `MAJOR.MINOR.PATCH` | The authoring UI's own default was `"1"`, so requiring it would orphan every seed written through that form |
| `backup.include` names a declared writable path | Nothing checked it before, so stale names exist in the wild, and loading beats refusing |

**The policy for schema 3: no field may become required, and no field's domain may
be narrowed.** Either forces schema 4. Closing a validation gap is a migration, not
a bugfix — ADR-076's amendment records a tightened rule crash-looping a control
plane over a bundle that was perfectly acceptable when it was installed.

---

## 12. Migrations

A seed's vocabulary changes. Stored values are keyed by name, so a rename silently
discards what every operator chose and reinstates the default.

That is not hypothetical. ADR-074 wanted to rename Valheim's `crossplay_flag` and
deliberately did not, because doing so would have turned crossplay back **on** for
every server where an operator had turned it off, with nothing to indicate it.

```yaml
variables:
  - name: crossplay
    renamed_from: [crossplay_flag]

migrations:
  - rename:  { from: instance, to: instance_id }
  - drop:    obsolete_flag
  - rewrite: { name: public, map: { "1": "true", "0": "false" } }
  - promote: { variable: max_players }        # variables -> settings
    note: adopted the settings block
```

`renamed_from` is sugar: it desugars into a `rename` at load, so there is exactly
one mechanism doing the carrying.

**Nothing is recorded per server** — no ledger, no applied-migrations column, no
state to get out of sync. That is affordable because every operation is
**idempotent by construction**, and validation is what guarantees it rather than
author care:

- `rename` applies only when `from` is present and `to` is absent.
- `drop` is trivially idempotent.
- `rewrite` is idempotent **because a map whose values intersect its keys is
  rejected at load**. That one rule buys the whole design; without it, stored
  values would drift a little on every rebuild, invisibly.
- `promote` applies only when the name is in variables and absent from settings.

Migrations run on the path that starts a server that already exists, so applying
them **cannot fail**. A malformed migration is rejected at *load*, where the
tolerant loader can skip the bundle and fall back a layer.

### 12.1 Converting a schema 2 seed

A schema 2 document is up-converted automatically on load, so an installed bundle
keeps working. The mechanical part:

| Schema 2 | Becomes |
|---|---|
| `install.method: download` + `filename` | `steps: [{op: download, url, into}]` |
| `install.method: download` + `archive` | `steps: [{op: download, ...}, {op: extract, ...}]` |
| `install.method: steamcmd` | `steps: [{op: steamcmd, app_id}]`, plus `image: {base: steamcmd}` — the image the agent was already defaulting to |
| `show_if: { variable: x }` | `show_if: { name: x }` |
| `backup.include: [""]` | `backup.include_root: true` |
| `image: "some/ref"` | `image: { ref: "some/ref" }` |

**`logs.ready` and `logs.crash` are dropped, not translated.** Nothing consumed
them, so dropping them changes no behaviour — while turning them into a `ready`
block would make readiness depend on a substring nobody verified, which is a
behaviour change wearing a conversion's clothes. They are also substrings, and
`ready.pattern` is a regexp: Paper's `"Done ("` is not even valid as one.

Four things are never converted automatically, because each changes behaviour and
is a judgement only an author can make: moving a stored value between the variable
and setting namespaces; promoting `ready.mode` off `immediate`; adopting
`image: {base: ...}`; and adopting `manage: once` or `patch`.

---

## 13. Templating

Templated fields are rendered with Go `text/template` against:

| Namespace | Is |
|---|---|
| `.Vars.<name>` | Every declared variable's resolved value |
| `.Settings.<name>` | Every declared setting's resolved value |
| `.Ports.<name>` | The **host port allocated** for that port name |
| `.Endpoint.<name>` | That port joined to the node's reachable address — what a player is given |
| `.ServerID`, `.NodeID`, `.ClusterID` | Identifiers |

Rendered fields: `install.steps[].url` / `.content` / `.set`, `containers[].command`
and `env` values, `cluster.args`, `config.files[].template` and `.set`,
`containers[].backup.pre` / `.post`, `connect.uri` / `.copy`.

**Every map is total.** Rendering uses `missingkey=error`, so a map missing a
declared key fails the render — on the path that starts an existing server. So the
maps are built from the seed's *declaration list*, never from stored values or
allocations, with the zero value where nothing is known. ADR-068 exists because
exactly this turned a routine seed update into a broken start handler.

`.Endpoint` is the one most likely to be sparse if built carelessly: a node's
address is legitimately unknown until its agent has connected, so it carries an
empty string rather than being absent.

Every templated field is dry-rendered at load against synthetic data built from
the seed's own declarations, so a typo fails when the seed is read rather than when
someone tries to use it.

---

## 14. Branding and connect

```yaml
branding:
  icon: icon.png
  logo: logo.png
  banner: banner.png
  accent: "#3f8f5b"
  steam_app_id: 892970

connect:
  uri: "steam://connect/{{.Endpoint.game}}"
  label: Join
  copy: "{{.Endpoint.game}}"
```

`branding` names image files **inside the bundle**. It is a closed key set on
purpose: an open-ended theme block becomes arbitrary CSS, and then a seed can break
the page it appears on.

A server's page leads with `banner`, falling back to `logo` when it declares no
banner, and `icon` is used wherever the seed or the server is listed.

`accent` is **reserved**: validated, and applied by nothing. Not because it is
hard, but because it is the one key that is not an image, and so the one that can
still break a page — the accent tokens travel as a set (`--accent`,
`--accent-wash`, `--accent-text`) and a seed supplying one colour of the three can
produce text unreadable against its own wash. When it lands it will never touch
semantic state colour: running is green whichever accent is active, because state
is information and an accent is decoration (ADR-054). A seed cannot make a crashed
server look healthy.

Set either the top-level `icon` (an emoji or an `http(s)://` URL) or
`branding.icon` (a bundle file). Both is an error rather than a precedence rule.

`steam_app_id` identifies this game's own Steam **client** — the app a player
installs to play — and is used only to fetch Store artwork for the editor and
to show a client-facing link. It is never used to install anything: an install
step's own `app_id` (§5.1) is a separate field, and the two are frequently
different (Valheim's dedicated-server tool has no store page while its base
game does, 896660 versus 892970 — ADR-051).

Assets are served from `GET /seeds/{id}/assets/{kind}`, where `kind` is `icon`,
`logo` or `banner`. **The request names a kind, never a filename** — the seed says
which file that is. So no request-supplied path reaches the filesystem, which
matters because a bundle can also hold an install script or a Dockerfile. Responses
carry a restrictive CSP and `nosniff`, since an SVG can carry script and this one
is served from the control plane's own origin. An unrecognised extension is a 404
rather than a guess; the allowed set is `.png`, `.jpg`, `.jpeg`, `.gif`, `.webp`,
`.svg`.

`connect` gives an operator a clickable join link, or an address to copy, instead
of a host and port to retype. It is rendered **per request**, never baked into a
pod: both fields template over `.Endpoint`, and a node's address can change or be
legitimately unknown (ADR-065).

**With no known node address the whole block renders nothing.** A bare port on the
allocations table reads as incomplete; a URI with an empty host does not. And a
template that fails to render yields nothing rather than failing the page — this is
a decoration on a page whose job is showing whether the server is running, and
load-time validation is where a broken template is meant to be caught.

Declare `uri` only for a scheme you have actually seen a client honour. Minecraft
registers none at all, so both bundled Minecraft seeds declare `copy` alone; an
unverified link that silently does nothing is worse than no link. A value that is
only knowable at runtime — Valheim's join code — is not a `connect` field but a
`logs.values` rule.

---

## 15. Authoring

### 15.1 The minimum valid seed

```yaml
id: my-game
schema: 3
name: My Game
version: "1.0.0"

containers:
  - role: game
    primary: true
    image: "some/image:tag"
    ports:
      - { name: game, protocol: tcp, default: 25565, kind: game }

server:
  writable_paths:
    - { from: "", to: /data }
```

`server.writable_paths` is not strictly required, but without it the server has
nowhere to persist state.

### 15.2 The contract for a creator tool

Any tool that writes seeds must:

1. **Validate through `internal/seed`, or against `schema.json`.** Do not
   reimplement the rules; they include cross-field checks a schema cannot express,
   and a tool that emits a seed `yggd` refuses is worse than no tool.
2. **Emit the canonical field order** (§3), and `image` as a mapping.
3. **Never silently drop what it cannot represent.** This is the rule the in-app
   authoring form follows: anything its guided fields cannot express forces the
   raw-YAML path rather than being lost on save. That failure has happened four
   times in this project already (ADR-050's and ADR-074's amendments, and ADR-077's
   final one) — and each time the field looked handled because nothing said it was
   not. Prefer an allowlist of what you *can* write over a list of exclusions: a
   field nobody taught the tool about is then unrepresentable by default.
4. **Bump `version` when behaviour changes**, and use `renamed_from` rather than
   renaming a control outright.
5. **Not write `.ygg-source.json`.** The catalog owns it.

### 15.3 `ygg-seed`

The reference implementation of that contract ships in this repository:

| Command | Does |
|---|---|
| `ygg-seed init -id <id>` | Scaffolds a bundle that **already validates**, so the first thing you change is the only thing that can be wrong |
| `ygg-seed validate <dir>` | Loads bundles exactly as yggd does. Takes one bundle or a library of them |
| `ygg-seed lint <dir>` | Reports what §11 says validation deliberately allows. `-strict` makes it an error |
| `ygg-seed migrate <dir>` | Rewrites schema 2 as schema 3, preserving comments and key order. A dry run until `-write` |
| `ygg-seed pack -channel <c>` | Builds a publishable catalog (§16). What CI runs |
| `ygg-seed import-egg <egg.json>` | Converts a Pelican or Pterodactyl egg, best-effort, reporting what it could not carry |

Two properties are worth relying on. `validate` calls the same loader the control
plane does, so it is not a second opinion. And `migrate` never converts a document
whose meaning it cannot preserve: it loads the result and compares it to what the
in-memory up-converter makes of the original, refusing rather than writing if they
differ.

`migrate` does **not** preserve blank lines between blocks — they are not part of
YAML's node model. Comments, key order and indentation survive; read the diff.

**Importing an egg is a starting point, not a conversion.** An egg's install is a
bash script, so it is saved into the bundle for you to translate into steps rather
than guessed at; an egg declares no ports, so one is declared for you and its
protocol is the first thing to check. Everything the converter could not carry is
printed rather than dropped.

### 15.4 Reserved identifiers

- Seed `id`: `^[a-z0-9]+(-[a-z0-9]+)*$`
- Variable, setting and log-value names: `^[a-zA-Z_][a-zA-Z0-9_]*$` — identifier
  rules, not kebab-case, because they are interpolated into commands
- A setting's `env` destination: `^[A-Z_][A-Z0-9_]*$`
- Container roles: `primary` is reserved on the wire for whichever container is
  marked primary

---

## 16. Publishing

A seed is packed into the catalog by `ygg-seed pack`, which loads every bundle
through the real loader first — so a seed `yggd` could not load fails on the
change that broke it, rather than on an operator's control plane.

**A floating release tag has exactly one writer.** For the project's own catalog
that is CI in the seeds repository, where the branch is the channel: push to
`develop` to publish edge, merge to `qa` or `main` to promote. A control plane
can publish too — the Publish action on `/seeds` — which is the path for an
operator with no CI; where CI publishes, `seeds.publish_repo` is left unset so
that button stays inert (ADR-081).

CI in the *source* repository runs the same packer over `seeds/library` as a
check and uploads nothing. That set is the **embedded** one a fresh install
starts from, so it has to stay loadable whether or not it is also published;
promoting a seed into it is a commit, not a sync.

Which repository a control plane reads is the `seeds.catalog_repo` setting,
defaulting to the project's own. Trust for a downloaded bundle is HTTPS plus the
published `SHA256SUMS`, not a signing key — the same either way, since a seed is
parsed and validated before it can replace anything, unlike an agent binary that
executes with Docker-socket access on every node.
