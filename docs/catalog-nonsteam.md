# Non-Steam catalog roadmap

> A candidate list of dedicated servers distributed by direct download, an
> installer, or an open-source release — never SteamCMD. Read on demand when
> picking the next seed to write.

This file tracks **candidates**, not status. What is actually built is always
`seeds/` on this branch — run `ls seeds/` rather than trusting a checkbox here
to go stale. When a game below gets a seed, delete its row; this file should
only ever list what is left.

A different install shape from the Steam catalog
([catalog-steam.md](catalog-steam.md)): `install.steps` here means
`download`/`extract` (or, for a few, a `write`/`patch` step around a vendor
installer jar) rather than `op: steamcmd`.

## Sourcing

- **Tier 1** combines two lists: the entries in LinuxGSM's own server list
  that carry **no** `appid=` at all (a direct-download install it has still
  run on Linux for years — the same actively-tested standard Tier 1 in the
  Steam catalog uses, just without SteamCMD in the loop) and
  [awesome-selfhosted's games list](https://awesome-selfhosted.net/tags/games.html),
  a curated, license-tagged, self-hosting-first directory.
- **Tier 2** is MMO server emulators — a private-server core for a game whose
  publisher never authorized a self-hosted server (World of Warcraft,
  EverQuest, Ultima Online, Tibia, RuneScape). Real, and popular in the
  self-hosting community, but a different kind of risk than anything above:
  the software itself is legitimate open source, but running it necessarily
  means standing up an unauthorized server for someone else's live game.
  Decide risk tolerance per project before starting one of these — this list
  is not the place that gets settled.
- **Tier 3** is smaller or niche titles with genuine but much smaller
  self-hosting communities — real candidates, just lower priority than
  anything above.

A handful of self-hostable browser party games (a quiz platform, a pictionary
clone, a chess server) turned up in the same awesome-selfhosted list and are
deliberately left off every tier here — outside this project's dedicated
game-server scope as it stands. Revisit if that scope should widen.

## Tier 1 — established, direct-download

| Game | Source |
|---|---|
| Factorio | official `.tar.xz` |
| FiveM (FXServer) | `runtime.fivem.net` |
| RedM (FXServer) | `runtime.fivem.net` |
| Minecraft: Forge server | installer jar |
| Minecraft: NeoForge server | installer jar |
| Minecraft: Fabric server | installer jar |
| Velocity (Minecraft proxy) | PaperMC downloads |
| Waterfall (Minecraft proxy) | PaperMC downloads |
| BungeeCord (Minecraft proxy) | Jenkins CI jar — verify it's still the recommended proxy before investing here; Velocity has largely superseded it |
| Luanti (Minetest) | official builds |
| OpenTTD | official builds |
| The Battle for Wesnoth | official builds |
| 0 A.D. | official builds |
| Veloren | official builds |
| Mindustry | GitHub releases (server jar) |
| Multi Theft Auto (MTA:SA) | official builds |
| San Andreas Multiplayer (SA-MP) | official builds |
| TeamSpeak 3 | official builds — voice, not a game, but a common fleet neighbor |
| Unreal Tournament 99 | direct download — verify current host |
| Unreal Tournament 2004 | direct download — verify current host |
| Unreal Tournament 3 | direct download — verify current host |
| Return to Castle Wolfenstein | direct download — verify current host |
| Wolfenstein: Enemy Territory | direct download — verify current host |
| ET: Legacy | official builds |
| Quake 2 | direct download — verify current host |
| Quake 3: Arena / ioquake3 | official builds |
| OpenArena | official builds |
| Quake World | direct download — verify current host |
| Zandronum | official builds |
| OpenRA | official builds |
| Warzone 2100 | official builds |
| Cube 2: Sauerbraten | official builds |
| Red Eclipse 2 | official builds |
| DDraceNetwork | official builds |
| piqueserver (OpenSpades) | PyPI / GitHub |
| Call of Duty | direct download — verify current host |
| Call of Duty 2 | direct download — verify current host |
| Call of Duty 4 | direct download — verify current host |
| Call of Duty: United Offensive | direct download — verify current host |
| Call of Duty: World at War | direct download — verify current host |
| Medal of Honor: Allied Assault | direct download — verify current host |
| Soldier Of Fortune 2: Gold Edition | direct download — verify current host |
| Battlefield 1942 | direct download — verify current host |
| Battlefield: Vietnam | direct download — verify current host |

The Minecraft ecosystem here is deliberately split three ways from what is
already built: Paper (plugins) already ships; Forge/NeoForge/Fabric (mods)
are a real gap with their own install mechanism per loader; the proxy layer
(Velocity/BungeeCord/Waterfall) is a different seed shape again — no game
world of its own, just routing between backend Minecraft servers, closer to
Empyrion's addon-container thinking than to a standalone game.

Several rows above (marked "verify current host") are old enough that their
official download location may no longer be the first-party site — check
before assuming a URL still resolves, the same caution
[seed-spec.md](seed-spec.md) already asks of a `download` install step.

## Tier 2 — legally grey (MMO emulators)

| Game |
|---|
| TrinityCore / AzerothCore (World of Warcraft) |
| EQEmu (EverQuest) |
| ServUO (Ultima Online) |
| Open Tibia (OTServ / Canary / TFS) |
| RSPS frameworks (RuneScape private servers) |

## Tier 3 — smaller or niche, real but lower priority

| Game | Source |
|---|---|
| Zero-K | official builds |
| Hypersomnia | GitHub releases |
| Suroi | self-hosted Node.js |
| Foundry VTT | official Node.js release — a virtual tabletop, not a traditional game server; verify it fits this project's model before starting |

## Suggested order

Tier 1, prioritizing whatever has the most immediate demand — Factorio and
the FiveM/RedM pair are the most-requested self-hosted targets outside the
Steam list entirely, and the three Minecraft mod loaders close a real,
frequently-asked-for gap next to the existing Paper seed. Tier 2 only with
eyes open about what it means to run one. Tier 3 whenever something on it
specifically comes up.
