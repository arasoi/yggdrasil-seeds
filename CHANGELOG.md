# Changelog

What changed in the catalog, newest first. Short on purpose: one line per seed change,
written for an operator, naming the seed and its new version.

Add the entry in the same change that bumps a seed's `version:`. Heading format is
`## <date>`; the publish workflow copies the three newest entries into the GitHub
release notes.

## 2026-11-20

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
