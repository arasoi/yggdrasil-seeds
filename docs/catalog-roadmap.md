# Catalog roadmap

> A candidate list for expanding the catalog, tiered by how confident we are
> in each one. Read on demand when picking the next seed to write.

This file tracks **candidates**, not status. What is actually built is always
`seeds/` on this branch — run `ls seeds/` rather than trusting a checkbox here
to go stale. When a game below gets a seed, delete its row; this file should
only ever list what is left.

It has two halves: Steam-distributed dedicated servers (SteamCMD), and
everything else (direct download, an installer, an open-source release).
The two need different sourcing, so each has its own tiers below.

## Steam-distributed

Tiered by how confident we are that each one runs on Linux without a
Proton/Wine wrapper.

### Sourcing

- **Tier 1** comes from [LinuxGSM](https://github.com/GameServerManagers/LinuxGSM)'s
  own `lgsm/data/serverlist.csv` cross-referenced against each game's
  `appid=` in `lgsm/config-default/config-lgsm/<gameserver>/_default.cfg`.
  LinuxGSM's codebase has no Wine/Proton invocation anywhere in it, so every
  entry it carries is a confirmed native-Linux SteamCMD depot — a maintained,
  actively-tested claim, not a guess.
- **Tier 2** AppIDs are confirmed against Steam's own `storesearch` /
  `appdetails` APIs (and, for the older ones, a historical scrape of every
  Steam app with "server" in its name), but LinuxGSM doesn't carry them, so
  Linux support is **unverified** — check with `steamcmd +login anonymous
  +app_info_print <appid>` (or the control plane's "Fetch from Steam" lookup)
  before assuming either way.
- **Tier 3** titles are believed to ship an official dedicated server based on
  general knowledge, but no AppID could be confirmed from the sources above.
  Some of these may install through the *base game's* AppID on a server
  branch rather than a separate free "Dedicated Server" tool app — that has
  to be established per game before writing anything.

Both APIs and LinuxGSM's list are snapshots from 2026-08-26 and will drift the
same way the seed catalog itself does (see architecture.md's own note on
that) — re-check rather than trusting an old row for a game with no seed yet.

### Already covered, not Steam

Minecraft Java (Paper), Minecraft Bedrock, and Vintage Story are already
shipped and intentionally excluded below — none of the three installs via
SteamCMD. They belong in spirit under "Non-Steam" below, but since they are
already built there is nothing left to track for them.

### Tier 1 — native Linux, LinuxGSM-verified

No Proton/Wine required for any of these. Sorted alphabetically; `376030`
(ARK: Survival Evolved), `2394010` (Palworld), `896660` (Valheim) and `294420`
(7 Days to Die) are already built and left off this table.

| Game | AppID |
|---|---|
| Action Half-Life | 90 |
| Action: Source | 985050 |
| American Truck Simulator | 2239530 |
| ARMA 3 | 233780 |
| Arma Reforger | 1874900 |
| Assetto Corsa | 302550 |
| Avorion | 565060 |
| Ballistic Overkill | 416880 |
| Barotrauma | 1026340 |
| Base Defense | 817300 |
| BATTALION: Legacy | 805140 |
| Black Mesa: Deathmatch | 346680 |
| Blade Symphony | 228780 |
| BrainBread | 90 |
| BrainBread 2 | 475370 |
| Chivalry: Medieval Warfare | 220070 |
| Codename CURE | 383410 |
| Colony Survival | 748090 |
| Core Keeper | 1963720 |
| Counter-Strike 1.6 | 90 |
| Counter-Strike 2 | 730 |
| Counter-Strike: Condition Zero | 90 |
| Counter-Strike: Global Offensive | 740 |
| Counter-Strike: Source | 232330 |
| Craftopia | 1670340 |
| Day of Defeat | 90 |
| Day of Defeat: Source | 232290 |
| Day of Dragons | 1088320 |
| Day of Infamy | 462310 |
| DayZ | 223350 |
| Deathmatch Classic | 90 |
| Don't Starve Together | 343050 |
| Double Action: Boogaloo | 317800 |
| Dystopia | 17585 |
| Eco | 739590 |
| Empires Mod | 460040 |
| Euro Truck Simulator 2 | 1948160 |
| Fistful of Frags | 295230 |
| Garry's Mod | 4020 |
| Half-Life 2: Deathmatch | 232370 |
| Half-Life Deathmatch: Source | 255470 |
| Half-Life: Deathmatch | 90 |
| HumanitZ | 2728330 |
| Hurtworld | 405100 |
| HYPERCHARGE: Unboxed | 1045940 |
| Insurgency | 237410 |
| Insurgency: Sandstorm | 581330 |
| IOSoccer | 673990 |
| Jabroni Brawl: Episode 3 | 869800 |
| Jedi Knight II: Jedi Outcast | 6030 |
| Just Cause 2 | 261140 |
| Just Cause 3 | 619960 |
| Killing Floor | 215360 |
| Killing Floor 2 | 232130 |
| Left 4 Dead | 222840 |
| Left 4 Dead 2 | 222860 |
| Military Conflict: Vietnam | 1136190 |
| MORDHAU | 629800 |
| Natural Selection | 90 |
| Natural Selection 2 | 4940 |
| Necesse | 1169370 |
| No More Room in Hell | 317670 |
| NS2: Combat | 313900 |
| Nuclear Dawn | 111710 |
| Onset | 1204170 |
| Operation: Harsh Doorstop | 950900 |
| Opposing Force | 90 |
| Pavlov VR | 622970 |
| Pirates Vikings & Knights II | 17575 |
| Project Cars | 332670 |
| Project Cars 2 | 413770 |
| Project Zomboid | 380870 |
| Quake 4 | 2210 |
| Quake Live | 349090 |
| Red Orchestra: Ostfront 41-45 | 223250 |
| Ricochet | 90 |
| Rising World | 339010 |
| Rust | 258550 |
| Satisfactory | 1690800 |
| SCP: Secret Laboratory | 996560 |
| SCP: Secret Laboratory ServerMod | 786920 |
| Soldat | 638500 |
| Soulmask | 3017300 |
| SourceForts Classic | 244310 |
| Squad | 403240 |
| Squad 44 (formerly Post Scriptum, same AppID) | 746200 |
| Starbound | 211820 |
| Stationeers | 600760 |
| StickyBots | 974130 |
| Survive the Nights | 1502300 |
| Sven Co-op | 276060 |
| Team Fortress 2 | 232250 |
| Team Fortress 2 Classified | 232250 |
| Team Fortress Classic | 90 |
| Teeworlds | 380840 |
| Terraria | 105600 |
| The Front | 2334200 |
| The Isle | 412680 |
| The Specialists | 90 |
| Tower Unite | 439660 |
| Unturned | 1110390 |
| Vampire Slayer | 90 |
| Warfork | 1136510 |
| Wurm Unlimited | 402370 |
| Zombie Master: Reborn | 244310 |
| Zombie Panic! Source | 17505 |

**A shared AppID is not a typo.** `90` is the classic GoldSrc "Half-Life
Dedicated Server" tool — a dozen mods above install through it and then need
a `-game <moddir>` launch flag plus the mod's own content on top, the same
way `244310` ("Source SDK Base 2013 Dedicated Server") backs several Source
mods. A seed for one of these needs that extra install step; it is not a
second copy of an existing game.

### Tier 2 — confirmed AppID, Linux unverified

Not in LinuxGSM's list, so treat native-Linux support as unknown until
checked. Several are known Tripwire/Offworld titles from the same lineage as
Tier 1 entries above (Squad, Killing Floor 2, Insurgency) that are simply
newer than LinuxGSM's coverage — worth checking first, as they may turn out
to be native-Linux too.

| Game | AppID | Note |
|---|---|---|
| Conan Exiles | 443030 | Funcom dropped official Linux dedicated server support around 2020 — likely needs Proton now |
| Space Engineers | 298740 | .NET, historically Windows-only |
| Medieval Engineers | 367970 | Same engine family as Space Engineers |
| The Forest | 556450 | Verify depot |
| Citadel: Forged With Fire | 489650 | Verify depot |
| Life is Feudal: Your Own | 320850 | Verify depot |
| Wreckfest | 361580 | Verify depot |
| RaceRoom Racing Experience | 354060 | Verify depot |
| Rising Storm 2: Vietnam | 418480 | Tripwire/UE3 — same lineage as Killing Floor 2/Insurgency (both native Linux) |
| Alien Swarm | 635 | Source engine — Valve titles are usually native Linux |
| Alien Swarm: Reactive Drop | 582400 | Source engine mod |
| America's Army: Proving Grounds | 203300 | Verify depot |
| Last Oasis | 920720 | Verify depot |
| Ground Branch | 476400 | Verify depot |

### Tier 3 — believed to exist, AppID unresolved

No confirmed dedicated-server AppID from either source above. Some of these
(the Unity-based survival games especially) may run their server through the
base game's own AppID on a specific branch rather than a separate free tool
app — that has to be established per game, most reliably by trying
`steamcmd +app_info_print <base game appid>` and reading the branch list,
before anything else is written.

| Game | Base game AppID (not the server) |
|---|---|
| V Rising | 1604030 |
| SCUM | 513710 |
| Icarus | 1149460 |
| Sons Of The Forest | 1326470 |
| Enshrouded | 1203620 |
| Abiotic Factor | 427410 |
| Smalland: Survive the Wilds | 768200 |
| Raft | 648800 |
| Green Hell | 815370 |
| Muck | 1625450 |
| Techtonica | 1457320 |
| Grounded | — |
| Frozen Flame | — |

`Grounded` has no confirmed base AppID recorded here and may not ship an
official dedicated server at all (Obsidian's multiplayer model differs from
the others in this tier) — confirm existence before treating it as a target.

### Suggested order

Tier 1 first: the Linux support question is already answered, so the only
work per seed is the ordinary install/config/ready-pattern authoring loop
[authoring.md](authoring.md) walks through. Within Tier 1, games sharing an
engine with something already built are cheapest — e.g. any Source or GoldSrc
title once one of that family exists as a seed, since the pod shape,
`RCON`/`stop` command style and log patterns mostly carry over.

Tier 2 next, prioritizing the Tripwire/Offworld titles most likely to be
native Linux despite being unverified. Tier 3 last, and only once its AppID
question is actually resolved — a Tier 3 row is a research task, not a seed
task, until then.

## Non-Steam

Dedicated servers distributed by direct download, an installer, or an
open-source release — never SteamCMD. A different install shape from the
Steam half above: `install.steps` here means `download`/`extract` (or, for a
few, a `write`/`patch` step around a vendor installer jar) rather than
`op: steamcmd`.

### Sourcing

- **Tier 1** combines two lists: the entries in LinuxGSM's own server list
  that carry **no** `appid=` at all (a direct-download install it has still
  run on Linux for years — the same actively-tested standard Tier 1 above
  uses, just without SteamCMD in the loop) and
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

### Tier 1 — established, direct-download

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

### Tier 2 — legally grey (MMO emulators)

| Game |
|---|
| TrinityCore / AzerothCore (World of Warcraft) |
| EQEmu (EverQuest) |
| ServUO (Ultima Online) |
| Open Tibia (OTServ / Canary / TFS) |
| RSPS frameworks (RuneScape private servers) |

### Tier 3 — smaller or niche, real but lower priority

| Game | Source |
|---|---|
| Zero-K | official builds |
| Hypersomnia | GitHub releases |
| Suroi | self-hosted Node.js |
| Foundry VTT | official Node.js release — a virtual tabletop, not a traditional game server; verify it fits this project's model before starting |

### Suggested order

Tier 1, prioritizing whatever has the most immediate demand — Factorio and
the FiveM/RedM pair are the most-requested self-hosted targets outside the
Steam list entirely, and the three Minecraft mod loaders close a real,
frequently-asked-for gap next to the existing Paper seed. Tier 2 only with
eyes open about what it means to run one. Tier 3 whenever something on it
specifically comes up.
