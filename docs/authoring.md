# Authoring a seed

> How to add a game to this repository, end to end. The format itself is in
> [seed-spec.md](seed-spec.md); this is the workflow, the order to do things in,
> and the mistakes that have actually been made.
>
> Read [testing.md](testing.md) before you publish. Validation proves a seed
> *loads*, which is a much weaker claim than that the game runs.

## Get the tool

`ygg-seed` validates a bundle against the same loader the control plane uses, so
a seed it accepts is a seed `yggd` accepts. It is a released binary — there is
nothing to build here.

```bash
curl -fsSLO https://github.com/arasoi/yggdrasil-releases/releases/download/release-latest/ygg-seed-linux-amd64
curl -fsSLO https://github.com/arasoi/yggdrasil-releases/releases/download/release-latest/SHA256SUMS
grep ' ygg-seed-linux-amd64$' SHA256SUMS | sha256sum -c -
chmod +x ygg-seed-linux-amd64 && sudo mv ygg-seed-linux-amd64 /usr/local/bin/ygg-seed
```

Verify the checksum rather than skipping it. It is the same trust level a control
plane applies to the bundles you are about to publish, and CI here does exactly
this.

Swap `release-latest` for `develop-latest` only when you need a format feature
that has not been promoted yet — and say so in the PR, because a seed that only
validates against an edge tool will fail for everyone whose control plane is on
stable.

Commands:

| Command | Does | Gate? |
|---|---|---|
| `ygg-seed init -id <id>` | Scaffolds a bundle that already validates | — |
| `ygg-seed validate <dir>` | Loads it exactly as `yggd` does | **Yes**, in CI |
| `ygg-seed lint <dir>` | Reports what validation deliberately allows | No — advice |
| `ygg-seed migrate <dir>` | Rewrites a schema 2 bundle as schema 3 | — |
| `ygg-seed import-egg <egg.json>` | Converts a Pelican/Pterodactyl egg, best-effort | — |
| `ygg-seed pack` | Builds a catalog. What CI runs | **Yes**, in CI |

Both `validate` and `lint` take either one bundle or a directory of them, so
`ygg-seed validate seeds` checks everything.

## Before you write anything

Answer these first. Each one is a decision the format makes you state, and
guessing at them is where most of the rework comes from.

1. **Does the container image already contain the game?** If yes, there is no
   `install` block at all. Minecraft Bedrock is this case — its image downloads
   the server itself at container start.
2. **How is the game distributed?** A plain download, a Steam depot, or several
   downloads. This picks your install steps and your base image.
3. **Is there an official Linux server build?** If not, the game needs Proton,
   which is a much bigger job — read the ARK seed before committing to it.
4. **What port does it bind, and is it TCP or UDP?** Getting this wrong is
   silent: the server starts, logs nothing wrong, and refuses every connection.
5. **How do you know it is up?** And have you *seen* that line in real output?
6. **How does it shut down cleanly?** A console command, or a signal.

If you cannot answer 4 and 5 from something you have actually run or read in a
real log, that is fine — declare `ready: {mode: immediate}` and a port you have
checked, and leave the rest out. An unverified pattern is worse than none.

## Start from something that works

```bash
ygg-seed init -id my-game -name "My Game" -dir seeds -port 25565 -protocol udp
ygg-seed validate seeds/my-game
```

The scaffold is deliberately a *working* seed rather than a template full of
placeholders: it validates immediately, so your first `validate` passes and you
change one thing at a time from something that works. A scaffold that does not
load teaches nothing about which of the ten things you then typed was wrong.

`-install download` and `-install steamcmd` (with `-app-id`) scaffold those
install shapes.

Then work outward in this order, validating after each step:

```
identity → container + port → install → config → variables/settings → ready/stop → the rest
```

Validating after **each** change is the whole technique. The loader dry-renders
every template against the seed's own declarations, so a typo in a command fails
the moment you introduce it rather than three edits later.

### Or start from a seed that already does something similar

Usually faster than starting blank. The five bundles here cover most shapes:

| Seed | Read it for |
|---|---|
| `minecraft-bedrock` | No install at all; settings with `env` destinations; migrations |
| `minecraft-java-paper` | Plain `download` install; whole-file config templates; `manage: once`; a large variable surface with groups and `show_if` |
| `valheim` | SteamCMD install; an offset-derived port; a verified `ready` pattern; `logs.values` extracting a join code |
| `vintage-story` | A two-download install (runtime + game); running on plain `base-linux`; a JSON config template |
| `ark-survival-ascended` | Shared install with writable overlays; clusters; Proton |

Copy the directory, change the `id` **and the directory name** to match, reset
`version:` to `1.0.0`, and delete the `branding:` block — its filenames point at
images that do not exist for your new seed.

## Choosing an image

```yaml
image: "itzg/minecraft-bedrock-server"          # third-party — the majority case
image: { ref: "eclipse-temurin:21-jre-alpine" } # the same thing, canonically
image: { base: steamcmd }                       # this project's own library
```

Use `ref` for any third-party image. Use `base` for this project's published base
images (`linux`, `steamcmd`, `steamcmd-proton`, `java`, `dotnet`), which resolves
to the right registry and channel at provision time — so a seed does not hardcode
an owner and a channel and get stuck on a tag built only from `main`.

Prefer a well-maintained official or community image over a base image plus an
install. Less to go wrong, and someone else keeps it current.

## Install steps

An install is an ordered list of typed operations. There is deliberately no shell
step: that would make a seed *code*, and no form could generate it.

```yaml
install:
  shared: false
  mount: { path: /game, mode: ro }
  steps:
    - op: download
      url: "https://example.com/server-{{.Vars.version}}.tar.gz"
      into: server.tar.gz
    - op: extract
      from: server.tar.gz
      strip_components: 1
```

Things that catch people:

- **`into` is required** on `download`. There is no basename default, because a
  templated URL's basename changes with a variable and the path your command
  references would move underneath it.
- **`extract` deletes the archive** after unpacking. Do not add a `move` or
  expect it to still be there.
- **`install.image` is required exactly when a step needs a container** — that is
  `steamcmd` — and **forbidden otherwise**. A plain download runs in the agent
  process with no image pull at all.
- **A field belonging to a different op is rejected, not ignored.** Writing
  `from:` where `into:` belongs is an error rather than a step that silently does
  nothing.
- **`shared: true` means the install is mounted read-only into every server that
  references it**, so it may not reference per-server data: no `.ServerID`,
  `.ClusterID`, `.Ports`, `.Settings` or `.Endpoint` in any step. Baking one
  server's value into shared files is silently wrong for all the others.

Use `shared: true` only when servers genuinely should share one copy — five ARK
maps off one 50 GB install. Two Valheim worlds have no more reason to share an
install than two Paper servers do.

## Variables or settings?

Two blocks, and the distinction is real:

> A **variable** shapes how the server is *built* — it reaches a command, an env
> value, an install step, or a mount. Changing one rebuilds the pod.
>
> A **setting** is written into the game's own configuration and *says where*.
> It needs no template line.

If you are unsure: does the value reach a command line or an install step?
Variable. Does it reach a config file or an env var only the game reads? Setting.

Settings are what let a game with forty-four documented keys avoid forty-four
template lines. Bedrock's 25 settings all have `env` destinations; Paper's
surface is still variables plus a whole-file template, which works and is simply
older.

Names share **one namespace** across both blocks — declaring the same name in
both is a load error, not a shadowing surprise.

## Ports

```yaml
ports:
  - { name: game,  protocol: udp, default: 2456, kind: game }
  - { name: query, protocol: udp, offset_from: game, offset: 1, kind: query }
```

- **`protocol` is required** and there is no default. A UDP game whose seed says
  `tcp` starts cleanly and refuses every connection.
- **`default` is not an allocation preference.** Allocation scans the node's
  configured port range and nothing else, because a range the operator set is
  their statement of which ports work on that host. This field documents the
  game's conventional port and supplies the authoring form's preview.
- **Therefore a player will not be on the conventional port.** If the game's
  client cannot be told a port, or the image starts the server itself and never
  reads your command, you must pass the allocated port in explicitly — Bedrock
  does this with `SERVER_PORT`.
- **`offset_from`** is for a game that hardcodes a relationship it gives you no
  flag to change, like Valheim's query port at `game_port + 1`. Do not use it for
  ports that merely happen to be adjacent.
- **Declare every port the game binds, including one nothing references.** ARK
  opens a second UDP socket at `game + 1` and derives the number itself: there is
  no argument, no ini key, and nothing in the seed to template it into. It still
  has to be declared, because a port the control plane does not know about is one
  it will allocate to somebody else — which is exactly what happened on a live
  fleet, where one map's raw socket was another server's game port and a new map
  was handed its own query port on `game + 1`. Both were silent: every server
  started, and the conflict only showed as players unable to connect.
  `offset_from` is what makes that safe, since a base and its siblings are
  reserved as one group (the pair moves together or not at all).
- **Order matters when a base has siblings.** Ports are allocated in declaration
  order, each base together with everything derived from it, so declare a base
  before the independent ports that follow it. Otherwise an independent port can
  be granted the number a sibling was going to need.
- Name the main port `game` and mark it `kind: game`, so the UI can show an
  operator the address that matters.

## Readiness, stop and crash

```yaml
ready:
  mode: log
  pattern: "Game server connected"
  timeout: 120s
```

Modes are `immediate` (the default), `log`, `port` and `healthcheck`.

**`mode: port` needs no game-specific knowledge at all, which makes it the right
first choice for a game you are adding blind.** It waits for the allocated port to
accept a connection, which is true of every game whether or not you know its log
format.

**Only write a `ready.pattern` you have seen in real output.** ARK's and
Valheim's are verified live and are fields; Paper's and Bedrock's are not, so
those seeds stay `immediate` and keep their candidates as YAML comments. A wrong
pattern delays a server by the whole timeout — recoverable, because the default
`on_timeout: warn` reports it running with a reason rather than stranding it, but
still wrong.

```yaml
stop:
  command: "stop"
  timeout: 60s
  then: SIGTERM
```

Most game servers want a console command rather than a signal, and losing that
distinction corrupts world saves. Get this right before you publish.

**Prefer no `crash:` rule at all to an unverified one.** The bar is higher than
readiness by more than it looks: a wrong readiness pattern *delays* a server, a
wrong crash pattern *stops a healthy one*. Neither seed here that once carried a
candidate still declares it — both are comments. `ygg-seed lint` warns about any
crash rule for this reason.

## Config files

Either generated whole from a template, or patched by key:

| `manage` | Does | Use for |
|---|---|---|
| `always` | Rewrites the whole file every rebuild | A file the seed owns outright |
| `once` | Writes it only if absent | A first-boot gate — `eula.txt` |
| `patch` | Sets only the named keys, preserving everything else | A file the game itself rewrites |

Two costs neither obvious nor recoverable if you pick wrong:

- **`always` discards an operator's hand edits on every rebuild.**
- **`once` fails silently forever.** A later template change never reaches a
  server that already has the file, and nothing about that server indicates it.

**Do not write a `config.files` entry for a file the container image owns and
rewrites at start.** Bedrock's image regenerates `server.properties` from
environment variables on every start, so a rendered file would be overwritten
before the server read it — its settings use `env` destinations instead.

**Watch the JSON patcher's typing.** It writes values as JSON strings, so a game
whose config has real numbers or booleans — Vintage Story's `MaxClients`, `Port`,
the `AllowXxx` flags — needs a whole-file template rather than `manage: patch`.
That is a concrete reason Vintage Story is shaped the way it is.

## Templating

Templated fields render against `.Vars`, `.Settings`, `.Ports`, `.Endpoint`,
`.ServerID`, `.NodeID` and `.ClusterID`.

**Every map is total** — rendering uses `missingkey=error`, and the maps are
built from the seed's *declaration list* rather than from stored values. So
referencing a variable you did not declare fails the render, and it fails on the
path that starts an existing server. The loader dry-renders everything at load
time so you find it immediately instead.

`command` is **not run through a shell**: no expansion, no globbing, no pipes.
Write `sh -c '...'` explicitly if you need them.

## Before you open a PR

```bash
ygg-seed validate seeds/my-game   # must pass
ygg-seed lint seeds/my-game       # should be clean
```

Then the part validation cannot do for you: **run it**. See
[testing.md](testing.md). A seed that validates and has never started a server is
a hypothesis.

Checklist in [contributing.md](contributing.md).

## Editing an existing seed

Two rules matter more than the rest:

**Bump `version:` whenever behaviour changes.** Nothing enforces it — the packer
can only reject a version it cannot *order*, not one that is merely stale — and
forgetting means nobody is ever offered your change.

**Never rename a variable or setting outright.** Stored values are keyed by name,
so a bare rename silently discards what every operator chose and reinstates the
default. Use `renamed_from`:

```yaml
- name: crossplay
  renamed_from: [crossplay_flag]
```

That is not hypothetical. Renaming Valheim's `crossplay_flag` without it would
have turned crossplay back **on** for every server where an operator had turned
it off, with nothing to indicate it.

The same care applies to removing one, changing a default, or narrowing a
`select`'s options — all of them change behaviour for servers that already exist.
See [conventions.md](conventions.md) for what counts as a breaking seed change.

## Converting a Pelican or Pterodactyl egg

```bash
ygg-seed import-egg path/to/egg.json -id my-game -dir seeds
```

**A starting point, not a conversion.** An egg's install is a bash script and a
seed's is a fixed vocabulary of typed operations, so the script is written into
the bundle for you to translate by hand rather than guessed at. Everything the
converter could not carry is printed rather than dropped — read that output.

Two things to check first, every time:

- **The declared port's protocol.** An egg declares no ports, so one is invented
  for you, and the protocol is a guess.
- **Egg variables become seed *settings*** with `env` destinations, since an egg
  variable is an environment variable the game reads. Some belong in `variables`
  instead — anything reaching the startup command does.

## Migrating a schema 2 bundle

```bash
ygg-seed migrate seeds/old-seed          # dry run — reports what would change
ygg-seed migrate seeds/old-seed -write
```

It edits a YAML node tree, so comments, key order and indentation survive.
**Blank lines between blocks do not** — they are not part of YAML's node model.
Read the diff.

It refuses rather than writes if the converted document does not match what the
in-memory converter makes of the original, so a conversion it cannot preserve
does not happen silently.

Four things are never converted automatically, because each is a judgement only
you can make: moving a stored value between the variable and setting namespaces;
promoting `ready.mode` off `immediate`; adopting `image: {base: ...}`; and
adopting `manage: once` or `patch`.
