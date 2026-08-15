# Seed field index

<!--
  GENERATED AND MIRRORED — do not edit here, and do not hand-edit it upstream
  either.

  This file is generated from the Go seed types by `make seedschema` in the
  control-plane repository, where a test fails if the committed copy has drifted
  from freshly generated output. It is copied here because that repository is
  private and this one is public.

  To change it, change the Go types upstream and regenerate. To refresh this
  copy, see contributing.md, "Keeping the mirrored docs current".
-->

Every field in the seed format, with the tier declared on the Go field it comes
from. See [seed-spec.md](seed-spec.md) for what any of it means, and
`internal/seed/schema.json` for the machine-readable form.

**This is a mirror** of a generated file, so it describes the format as of the
`ygg-seed` release it was copied from. If it lists a field your `ygg-seed`
rejects, this copy is ahead of your tool; if the tool accepts one this file does
not list, it is behind. `ygg-seed validate` settles it either way.

| Tier | Meaning |
|---|---|
| `stable` | Has a consumer, and will not change shape without a schema version bump. |
| `provisional` | Has a consumer, but its shape may still change within this schema version. |
| `reserved` | Specified and validated, with **no consumer**: setting it changes nothing about a running server. |

## The document

| Key | Type | Required | Tier |
|---|---|---|---|
| `schema` | integer | yes | `stable` |
| `id` | string | yes | `stable` |
| `name` | string | yes | `stable` |
| `version` | string |  | `stable` |
| `description` | string |  | `stable` |
| `icon` | string |  | `stable` |
| `branding` | Branding |  | `provisional` |
| `architectures` | list of string |  | `stable` |
| `install` | Install |  | `stable` |
| `server` | Server |  | `stable` |
| `cluster` | Cluster |  | `stable` |
| `containers` | list of Container |  | `stable` |
| `variables` | list of Variable |  | `stable` |
| `groups` | list of Group |  | `stable` |
| `settings` | list of Setting |  | `provisional` |
| `config` | Config |  | `stable` |
| `ready` | Ready |  | `provisional` |
| `crash` | Crash |  | `provisional` |
| `stop` | Stop |  | `stable` |
| `logs` | LogRules |  | `stable` |
| `connect` | Connect |  | `provisional` |
| `backup` | Backup |  | `stable` |
| `migrations` | list of Migration |  | `provisional` |

## Backup

Names which writable paths a backup includes.

| Key | Type | Required | Tier |
|---|---|---|---|
| `include` | list of string |  | `stable` |
| `include_root` | boolean |  | `stable` |

## Branding

Names image files inside the seed's own bundle.

| Key | Type | Required | Tier |
|---|---|---|---|
| `icon` | string |  | `provisional` |
| `logo` | string |  | `provisional` |
| `banner` | string |  | `provisional` |
| `accent` | string |  | `reserved` |
| `steam_app_id` | integer |  | `provisional` |

## Cluster

Describes how a seed's servers may join a cluster (ADR-020).

| Key | Type | Required | Tier |
|---|---|---|---|
| `supported` | boolean |  | `stable` |
| `mount` | string |  | `stable` |
| `args` | list of string |  | `stable` |

## Condition

Makes one control appear, or one destination be written, only when another value holds (or does not hold) a given value.

| Key | Type | Required | Tier |
|---|---|---|---|
| `name` | string | yes | `provisional` |
| `equals` | string |  | `provisional` |
| `not_equals` | string |  | `provisional` |

## Config

Is the set of files a seed manages inside a server's writable directory.

| Key | Type | Required | Tier |
|---|---|---|---|
| `files` | list of ConfigFile |  | `stable` |

## ConfigFile

Is one file a seed manages inside a server's writable directory.

| Key | Type | Required | Tier |
|---|---|---|---|
| `path` | string | yes | `stable` |
| `template` | string |  | `stable` |
| `source_path` | string |  | `stable` |
| `manage` | *(unset)* \| `always` \| `once` \| `patch` |  | `provisional` |
| `parser` | *(unset)* \| `properties` \| `json` \| `yaml` \| `ini` \| `xml` |  | `provisional` |
| `set` | map of string |  | `provisional` |
| `if` | Condition |  | `provisional` |
| `importable` | boolean |  | `provisional` |

## Connect

Describes how a player reaches a server built from this seed.

| Key | Type | Required | Tier |
|---|---|---|---|
| `uri` | string |  | `provisional` |
| `label` | string |  | `provisional` |
| `copy` | string |  | `provisional` |

## Container

Describes one container in the seed's pod (ADR-017).

| Key | Type | Required | Tier |
|---|---|---|---|
| `role` | string | yes | `stable` |
| `primary` | boolean |  | `stable` |
| `optional` | boolean |  | `provisional` |
| `name` | string |  | `provisional` |
| `description` | string |  | `provisional` |
| `image` | string or ImageRef |  | `stable` |
| `command` | string |  | `stable` |
| `env` | map of string |  | `stable` |
| `workdir` | string |  | `stable` |
| `ports` | list of Port |  | `stable` |
| `volumes` | list of Volume |  | `stable` |
| `depends_on` | list of Dependency |  | `stable` |
| `healthcheck` | HealthCheck |  | `stable` |
| `open_stdin` | boolean |  | `stable` |
| `backup` | ContainerBackup |  | `stable` |

## ContainerBackup

Names commands run inside this container around a backup's archive step (ADR-023) — pg_dump and its cleanup. Both are rendered the same way Command is and run as "sh -c <rendered>" (ADR-023 examples use shell redirection). A hook whose container is not running when a backup runs is skipped rather than failing the backup.

| Key | Type | Required | Tier |
|---|---|---|---|
| `pre` | string |  | `stable` |
| `post` | string |  | `stable` |

## Crash

Names how a server is detected as crashed beyond its process exiting.

| Key | Type | Required | Tier |
|---|---|---|---|
| `mode` | *(unset)* \| `none` \| `log` |  | `provisional` |
| `pattern` | string |  | `provisional` |

## Dependency

Gates a container's startup on another (ADR-019).

| Key | Type | Required | Tier |
|---|---|---|---|
| `role` | string | yes | `stable` |
| `condition` | `started` \| `healthy` |  | `stable` |

## Destination

Is where a setting's value is written. Exactly one of (File and Key), Env, or Arg.

| Key | Type | Required | Tier |
|---|---|---|---|
| `file` | string |  | `provisional` |
| `key` | string |  | `provisional` |
| `env` | string |  | `provisional` |
| `container` | string |  | `provisional` |
| `arg` | string |  | `reserved` |
| `if` | Condition |  | `provisional` |

## Group

Carries optional presentation metadata for a form group.

| Key | Type | Required | Tier |
|---|---|---|---|
| `name` | string | yes | `stable` |
| `description` | string |  | `stable` |
| `collapsed` | boolean |  | `stable` |

## HealthCheck

Is a container's own liveness probe.

| Key | Type | Required | Tier |
|---|---|---|---|
| `command` | string |  | `stable` |
| `interval` | string |  | `stable` |
| `timeout` | string |  | `stable` |
| `retries` | integer |  | `stable` |

## ImageRef

Names a container image, either verbatim or symbolically.

| Key | Type | Required | Tier |
|---|---|---|---|
| `ref` | string |  | `stable` |
| `base` | string |  | `provisional` |
| `channel` | *(unset)* \| `develop` \| `qa` \| `release` |  | `provisional` |
| `tag` | string |  | `reserved` |

## Install

Describes how a seed's game files are materialised on a node.

| Key | Type | Required | Tier |
|---|---|---|---|
| `shared` | boolean |  | `stable` |
| `mount` | Mount |  | `stable` |
| `image` | string or ImageRef |  | `stable` |
| `steps` | list of Step |  | `stable` |

## LogEvent

Recognises one well-known occurrence in a server's output.

| Key | Type | Required | Tier |
|---|---|---|---|
| `event` | `join` \| `leave` \| `chat` \| `update_available` | yes | `provisional` |
| `pattern` | string | yes | `provisional` |

## LogRules

Names what to pull out of a server's own output.

| Key | Type | Required | Tier |
|---|---|---|---|
| `values` | list of LogValue |  | `stable` |
| `events` | list of LogEvent |  | `provisional` |

## LogValue

Extracts one named fact from the primary container's output — something a player needs that only the running server knows, and that is printed rather than configured. Valheim's six-digit join code is the case this exists for: it changes on every restart and appears nowhere else.

| Key | Type | Required | Tier |
|---|---|---|---|
| `name` | string | yes | `stable` |
| `pattern` | string | yes | `stable` |
| `label` | string |  | `provisional` |
| `fleet` | boolean |  | `provisional` |

## Migration

Carries a server's stored values forward when a seed's own vocabulary changes.

| Key | Type | Required | Tier |
|---|---|---|---|
| `rename` | Rename |  | `provisional` |
| `drop` | string |  | `provisional` |
| `rewrite` | Rewrite |  | `provisional` |
| `promote` | Promote |  | `provisional` |
| `note` | string |  | `provisional` |

## Mount

Describes where an install lands inside its containers.

| Key | Type | Required | Tier |
|---|---|---|---|
| `path` | string | yes | `stable` |
| `mode` | *(unset)* \| `ro` \| `rw` |  | `stable` |

## Option

Is one choice offered by a select or radio control.

| Key | Type | Required | Tier |
|---|---|---|---|
| `value` | string | yes | `stable` |
| `label` | string |  | `stable` |
| `description` | string |  | `reserved` |

## Port

Declares one port a container needs.

| Key | Type | Required | Tier |
|---|---|---|---|
| `name` | string | yes | `stable` |
| `protocol` | `tcp` \| `udp` |  | `stable` |
| `kind` | *(unset)* \| `game` \| `query` \| `rcon` \| `web` \| `voice` \| `other` |  | `provisional` |
| `default` | integer |  | `provisional` |
| `publish` | boolean |  | `reserved` |
| `offset_from` | string |  | `stable` |
| `offset` | integer |  | `stable` |

## Promote

Moves a stored value from the variables namespace to settings.

| Key | Type | Required | Tier |
|---|---|---|---|
| `variable` | string | yes | `provisional` |

## Ready

Decides when a started server is reported running.

| Key | Type | Required | Tier |
|---|---|---|---|
| `mode` | *(unset)* \| `immediate` \| `log` \| `port` \| `healthcheck` |  | `provisional` |
| `pattern` | string |  | `provisional` |
| `port` | string |  | `provisional` |
| `timeout` | string |  | `provisional` |
| `on_timeout` | *(unset)* \| `warn` \| `fail` |  | `provisional` |

## Rename

Moves a stored value from one name to another.

| Key | Type | Required | Tier |
|---|---|---|---|
| `from` | string | yes | `provisional` |
| `to` | string | yes | `provisional` |

## Rewrite

Maps a control's old stored values onto new ones.

| Key | Type | Required | Tier |
|---|---|---|---|
| `name` | string | yes | `provisional` |
| `map` | map of string | yes | `provisional` |

## Server

Describes what a server built from this seed needs on top of a shared install.

| Key | Type | Required | Tier |
|---|---|---|---|
| `writable_paths` | list of WritablePath |  | `stable` |
| `file_denylist` | list of string |  | `provisional` |

## Setting

Is one piece of the game's own configuration.

| Key | Type | Required | Tier |
|---|---|---|---|
| `name` | string | yes | `stable` |
| `default` | string |  | `stable` |
| `label` | string |  | `stable` |
| `description` | string |  | `stable` |
| `group` | string |  | `stable` |
| `type` | *(unset)* \| `text` \| `password` \| `number` \| `range` \| `select` \| `radio` \| `bool` |  | `stable` |
| `options` | list of Option |  | `stable` |
| `min` | number |  | `stable` |
| `max` | number |  | `stable` |
| `step` | number |  | `stable` |
| `true_value` | string |  | `stable` |
| `false_value` | string |  | `stable` |
| `show_if` | Condition |  | `stable` |
| `generate` | *(unset)* \| `password` \| `uuid` \| `hex` |  | `provisional` |
| `length` | integer |  | `provisional` |
| `renamed_from` | list of string |  | `provisional` |
| `deprecated` | string |  | `reserved` |
| `to` | Destination | yes | `provisional` |
| `optional` | boolean |  | `provisional` |

## Step

Is one operation in an install.

| Key | Type | Required | Tier |
|---|---|---|---|
| `op` | `download` \| `extract` \| `steamcmd` \| `mkdir` \| `copy` \| `move` \| `chmod` \| `write` \| `patch` \| `start_app` \| `wait_ready` \| `stop_app` | yes | `stable` |
| `name` | string |  | `stable` |
| `if` | Condition |  | `provisional` |
| `url` | string |  | `stable` |
| `into` | string |  | `stable` |
| `from` | string |  | `stable` |
| `to` | string |  | `provisional` |
| `archive` | *(unset)* \| `auto` \| `zip` \| `targz` |  | `stable` |
| `strip_components` | integer |  | `provisional` |
| `app_id` | integer |  | `stable` |
| `beta` | string |  | `provisional` |
| `beta_password` | string |  | `provisional` |
| `validate` | boolean |  | `provisional` |
| `path` | string |  | `provisional` |
| `mode` | string |  | `provisional` |
| `content` | string |  | `provisional` |
| `parser` | `properties` \| `json` \| `yaml` \| `ini` \| `xml` |  | `provisional` |
| `set` | map of string |  | `provisional` |
| `if_missing` | boolean |  | `provisional` |
| `command` | string |  | `reserved` |
| `timeout` | string |  | `reserved` |
| `then` | string |  | `reserved` |
| `ready` | Ready |  | `reserved` |

## Stop

Describes how to bring a server down gracefully.

| Key | Type | Required | Tier |
|---|---|---|---|
| `command` | string |  | `stable` |
| `timeout` | string |  | `stable` |
| `then` | string |  | `stable` |

## Variable

Is one input that shapes how a server is built.

| Key | Type | Required | Tier |
|---|---|---|---|
| `name` | string | yes | `stable` |
| `default` | string |  | `stable` |
| `label` | string |  | `stable` |
| `description` | string |  | `stable` |
| `group` | string |  | `stable` |
| `type` | *(unset)* \| `text` \| `password` \| `number` \| `range` \| `select` \| `radio` \| `bool` |  | `stable` |
| `options` | list of Option |  | `stable` |
| `min` | number |  | `stable` |
| `max` | number |  | `stable` |
| `step` | number |  | `stable` |
| `true_value` | string |  | `stable` |
| `false_value` | string |  | `stable` |
| `show_if` | Condition |  | `stable` |
| `generate` | *(unset)* \| `password` \| `uuid` \| `hex` |  | `provisional` |
| `length` | integer |  | `provisional` |
| `renamed_from` | list of string |  | `provisional` |
| `deprecated` | string |  | `reserved` |
| `editable` | boolean |  | `stable` |
| `required` | boolean |  | `stable` |

## Volume

Is a sidecar's own named volume, distinct from a shared install mount or a server's writable paths.

| Key | Type | Required | Tier |
|---|---|---|---|
| `from` | string |  | `stable` |
| `to` | string |  | `stable` |

## WritablePath

Bind-mounts a server's own directory over part of a read-only install (ADR-018).

| Key | Type | Required | Tier |
|---|---|---|---|
| `from` | string |  | `stable` |
| `to` | string |  | `stable` |
