# Changelog

What changed in the catalog, newest first. Short on purpose: one line per seed change,
written for an operator, naming the seed and its new version.

Add the entry in the same change that bumps a seed's `version:`. Heading format is
`## <date>`; the publish workflow copies the three newest entries into the GitHub
release notes.

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
