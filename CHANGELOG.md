# Changelog

What changed in the catalog, newest first. Short on purpose: one line per seed change,
written for an operator, naming the seed and its new version.

Add the entry in the same change that bumps a seed's `version:`. Heading format is
`## <date>`; the publish workflow copies the three newest entries into the GitHub
release notes.

## 2026-11-28 (5)

- **dune-awakening 0.4.5**: each map server is given its map first on the command line, so the game no longer mistakes the RabbitMQ host name for the map to load and crash.

## 2026-11-28 (4)

- **dune-awakening 0.4.4**: the battlegroup director and the map servers are told the database's name, instead of the director looking for a version-named database that is never created.

## 2026-11-28 (3)

- **dune-awakening 0.4.3**: the map servers start through the image's own launcher (/home/dune/run.sh), which Funcom's current build uses in place of the removed run_server.sh, with the pod address it expects set first.

## 2026-11-28 (2)

- **dune-awakening 0.4.2**: the database schema step points Funcom's tool at the PostgreSQL client already in its image and skips its own pre-update dump (the image has no pg_dump), instead of trying to install a Windows-only PostgreSQL and stopping the battlegroup from starting.

## 2026-11-28

- **dune-awakening 0.4.1**: the battlegroup images are pinned to the tag Funcom's current depot ships (2181988-0-shipping). Servers installed from today's depot failed to start because the images loaded under that tag while the seed asked for the old one. Install the update, then rebuild the server.

## 2026-11-27 (3)

- **fivem 1.6.0**: txAdmin gets a tab on the server's page, reached through Yggdrasil rather than the node's address. It needs yggdrasil 0.81.0 with a wildcard addon origin (`addon_public_url: https://*.<domain>`); without one the tab explains what to set up.

## 2026-11-27 (2)

- **fivem 1.5.0**: the Adminer add-on is gone; the bundled MariaDB is browsed from Yggdrasil's own Database tab instead, which never publishes the database. Needs yggdrasil 0.80.0, without which the server has no database tab at all.
- **dune-awakening 0.4.0**: the CloudBeaver add-on is gone, replaced the same way for its PostgreSQL. Needs yggdrasil 0.80.0.

## 2026-11-27

- **fivem 1.4.2**: stopping, restarting or rebuilding a server no longer waits 30 seconds for a console command txAdmin ignores; it signals txAdmin straight away, which shuts FXServer down itself.

## 2026-11-26 (4)

- **palworld 1.3.1**: server name, description, passwords, advertised IP, region and ban-list URL now refuse a double quote or backslash on save, instead of writing a PalWorldSettings.ini the game cannot parse. Needs yggdrasil 0.78.0.
- **euro-truck-simulator-2 1.0.1**: server name, description, welcome message, join password and login token refuse a double quote or backslash, which would break server_config.sii.
- **american-truck-simulator 1.0.1**: the same.

## 2026-11-26 (3)

- **ark-survival-ascended 5.10.0**: stopping, restarting or updating a server now saves the world first (over RCON), instead of losing play since the last autosave. Needs a server admin password and agents on yggdrasil 0.77.0.
- **ark-survival-evolved 1.6.0**: the same RCON save-and-exit on stop.

## 2026-11-26 (2)

- **core-keeper 1.0.1**: names, passwords and other free-text values with spaces or quotes no longer break the launch command.
- **counter-strike-2 1.0.2**: names, passwords and other free-text values with spaces or quotes no longer break the launch command.
- **garrys-mod 1.0.2**: names, passwords and other free-text values with spaces or quotes no longer break the launch command.
- **killing-floor-2 1.0.2**: names, passwords and other free-text values with spaces or quotes no longer break the launch command.
- **left-4-dead-2 1.2.3**: names, passwords and other free-text values with spaces or quotes no longer break the launch command.
- **mordhau 1.0.2**: names, passwords and other free-text values with spaces or quotes no longer break the launch command.
- **necesse 1.0.3**: names, passwords and other free-text values with spaces or quotes no longer break the launch command.
- **project-zomboid 1.2.1**: names, passwords and other free-text values with spaces or quotes no longer break the launch command.
- **rust 1.0.5**: names, passwords and other free-text values with spaces or quotes no longer break the launch command.
- **team-fortress-2 1.0.7**: names, passwords and other free-text values with spaces or quotes no longer break the launch command.
- **valheim 2.4.2**: names, passwords and other free-text values with spaces or quotes no longer break the launch command.
- **dune-awakening 0.3.2**: the same launch-command fix, and backups now include a pg_dump of the database beside the live files.
- **7-days-to-die 1.3.1**: a name, password or description containing `&`, `<` or quotes no longer produces an invalid serverconfig.xml.
- **empyrion 1.1.2**: a name, password or description containing quotes no longer produces an invalid dedicated.yaml.

## 2026-11-26

- **ark-survival-ascended 5.9.1**: the admin/RCON password is generated per new server instead of defaulting to "changeme". A cluster member that was only inheriting the old default now has no admin password (RCON off) until you set one.
- **ark-survival-evolved 1.5.1**: same change as ASA, and the admin password field is now masked.
- **valheim 2.4.1**: the server password is generated per new server instead of defaulting to "changeme123". Existing servers keep theirs.
- **fivem 1.4.1**: backups work again. The database dump now goes into the database volume, and the password is passed safely.
- **minecraft-java-paper 3.1.1**: backups work. The seed declares what to back up (the whole server directory).
- **minecraft-bedrock 4.1.1**: backups work, as for Paper. Archives include the server binaries that live beside the worlds.

## 2026-11-24

- **pavlov-vr 1.0.1**: the API key is optional; without one the server runs unlisted, for direct connections.
- **rising-world 1.0.0**: new seed. Native Linux (Unity) server; server.properties settings from the UI.
- **the-isle 1.0.0**: new seed. The Isle Evrima's native Linux server; Game.ini settings from the UI.
- **pavlov-vr 1.0.0**: new seed. Native Linux server; needs Yggdrasil 0.76.4's base-steamcmd and a Pavlov API key.
- **euro-truck-simulator-2 1.0.0**: new seed. Native Linux convoy server; starts with default server_packages until you upload your own.
- **american-truck-simulator 1.0.0**: new seed. Same shape as Euro Truck Simulator 2.
- **squad 1.0.1**: new seed. Native Linux server; Server.cfg settings from the UI, the rest of ServerConfig in Files.

## 2026-11-23

- **dont-starve-together 1.0.1**: new seed. Master and Caves shards in one container; needs a Klei cluster token.
- **scp-secret-laboratory 1.0.1**: new seed. Native Linux server under LocalAdmin.
- **craftopia 1.0.1**: new seed. Native Linux dedicated server; ServerSetting.ini settings from the UI.
- **avorion 1.0.0**: new seed. Native Linux dedicated server; needs Yggdrasil 0.76.1's base-steamcmd.
- **mordhau 1.0.1**: ready now waits for the real map, and the console no longer stops after startup.

## 2026-11-20

- **humanitz 1.0.0**: new seed. Native Linux dedicated server; server.ini settings from the UI.
- **mordhau 1.0.0**: new seed. Native Linux dedicated server (not the Wine build).
- **killing-floor-2 1.0.1**: new seed. Native Linux dedicated server on one shared install per node.

## 2026-11-18

- **barotrauma 1.0.0**: new seed. Native Linux dedicated server; settings are made in game or in
  serversettings.xml.
- **counter-strike-2 1.0.1**: new seed. One shared install per node; your own cfg/server.cfg runs on
  every start.
- **soulmask 1.0.1**: new seed. Native Linux dedicated server with a generated GM password.
- **arma-reforger 1.0.1**: new seed. Native Linux dedicated server; the Direct Join Code shows on the
  server's card, and the scenario field lists every base-game scenario.
- **unturned 1.0.2**: new seed. Native Linux dedicated server; the Server Code players join with
  shows on the server's card, and Stop saves the world.
- **the-front 1.0.1**: new seed, KNOWN BROKEN: the published Linux server build crashes on start
  ("Could not find SuperStruct BP_GameMode_Game_C"). Kept so it works once the developer fixes it.
- **core-keeper 1.0.0**: new seed. Native Linux dedicated server on a virtual display; the Game ID
  players join with shows on the server's card. Needs Yggdrasil 0.75.3's base-steamcmd image.
- **necesse 1.0.2**: new seed. Native Linux dedicated server on its bundled Java runtime;
  shows the running game version.
- **project-zomboid 1.2.0**: new seed. Native Linux dedicated server with a generated admin password
  and the common server.ini settings (listing, password, PvP, saving, Workshop mods, RCON).
- **satisfactory 1.0.1**: new seed. Native Linux dedicated server; claim it and set the admin
  password from the game's Server Manager. Shows the running build on the server's card.
- **runescape-dragonwilds 0.7.1**: now has its icon, logo and banner, so it no longer shows
  as a placeholder card. Every other seed already had artwork.

## 2026-11-16

- **ark-survival-ascended 5.9.0** and **ark-survival-evolved 1.5.0**: `map` and `session_name`
  are now per-server controls. A cluster never offers or stores them, so each member keeps
  its own. Needs Yggdrasil 0.74.0 or later to take effect; an older control plane ignores it.
