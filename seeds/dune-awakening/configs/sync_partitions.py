#!/usr/bin/env python3
"""Fill the battlegroup's world_partition table from Funcom's own world template.

Funcom's database operator does this in its Kubernetes setup: the BattleGroup
resource that scripts/setup/world.sh creates from
scripts/setup/templates/world-template.yaml lists every map's partitions
under spec.database.template.spec.deployment.spec.worldPartitions, and the
operator writes them into world_partition. Without them a map server loops
forever on "no partition definition". Yggdrasil runs the containers without
that operator, so this runs in their place on every start (the container is
once: true), reading the same template from the installed depot so a Funcom
update that adds or moves a partition reaches the database with no seed change.

It only inserts partitions that are missing, keyed by the template's own ids
(the map servers are started with -PartitionIndex=<id>), and never touches a
row that exists: a row's server assignment belongs to the director. A row
whose map disagrees with the template is reported, not rewritten.
"""

import json
import os
import re
import sys

import psycopg2

TEMPLATE = os.environ.get(
    "DUNE_WORLD_TEMPLATE", "/game/scripts/setup/templates/world-template.yaml"
)


def parse_partitions(text):
    """Return the worldPartitions entries as flat dicts with a "map" key.

    A small reader for the one block it needs, rather than a YAML library:
    the template carries {PLACEHOLDER} values that are not valid YAML until
    world.sh substitutes them, and the db-utils image is not promised to ship
    a YAML parser.
    """
    lines = text.splitlines()
    start = indent = None
    for i, line in enumerate(lines):
        if line.strip() == "worldPartitions:":
            start, indent = i, len(line) - len(line.lstrip())
            break
    if start is None:
        raise SystemExit("no worldPartitions block in " + TEMPLATE)

    parts, current_map, current = [], None, None
    for line in lines[start + 1:]:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        depth = len(line) - len(line.lstrip())
        # YAML lets a list sit at its key's own indent, which the template's
        # does; the block ends at the first line that is neither deeper nor
        # one of those items.
        if depth < indent or (depth == indent and not stripped.startswith("-")):
            break
        found = re.match(r"-\s*map:\s*(.*)$", stripped)
        if found:
            current_map = found.group(1).strip().strip("'\"")
            current = None
            continue
        if stripped == "partitions:":
            continue
        if stripped.startswith("- "):
            current = {"map": current_map}
            parts.append(current)
            stripped = stripped[2:].strip()
        if current is None or ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        current[key.strip()] = value.strip().strip("'\"")
    return parts


def literal_block(text, key):
    """The body of a `key: |-` block scalar, dedented, or None if absent."""
    lines = text.splitlines()
    out, key_indent, base = None, None, None
    for line in lines:
        if out is None:
            found = re.match(r"^(\s*)" + re.escape(key) + r":\s*\|-?\s*$", line)
            if found:
                out, key_indent = [], len(found.group(1))
            continue
        if not line.strip():
            out.append("")
            continue
        depth = len(line) - len(line.lstrip())
        if depth <= key_indent:
            break
        if base is None:
            base = depth
        out.append(line[base:])
    if out is None:
        return None
    return "\n".join(out).strip("\n")


def check_director_ini(template_text):
    """Warn when the director.ini this seed ships no longer matches Funcom's.

    The director's image keeps its own entrypoint, so the seed cannot extract
    the file at the director's start the way this script reads partitions; it
    ships a copy instead, and this is where a Funcom update that changes the
    original shows up.
    """
    path = os.environ.get("DUNE_SEED_DIRECTOR_INI", "/ygg/director.ini")
    theirs = literal_block(template_text, "director.ini")
    if theirs is None or not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as handle:
        ours = handle.read().strip("\n")
    normalise = lambda s: [line.rstrip() for line in s.splitlines()]
    if normalise(ours) != normalise(theirs):
        print(
            "WARNING: Funcom's director.ini in " + TEMPLATE + " differs from the one this"
            " seed ships; the seed's copy is in use until the seed is updated"
        )


def number(value, default):
    """A template coordinate as an int when it is whole, else a float."""
    if value in (None, ""):
        return default
    as_float = float(value)
    return int(as_float) if as_float.is_integer() else as_float


def main():
    with open(TEMPLATE, encoding="utf-8") as handle:
        template_text = handle.read()
    check_director_ini(template_text)
    parts = parse_partitions(template_text)
    if not parts:
        raise SystemExit("worldPartitions in " + TEMPLATE + " lists no partitions")

    conn = psycopg2.connect(
        host=os.environ.get("PGHOST", "postgres"),
        port=int(os.environ.get("PGPORT", "5432")),
        user=os.environ.get("PGUSER", "dune"),
        password=os.environ["PGPASSWORD"],
        dbname=os.environ.get("PGDATABASE", "dune"),
    )
    added = 0
    with conn, conn.cursor() as cur:
        cur.execute("SET search_path TO dune, public")
        cur.execute("SELECT partition_id, map FROM world_partition")
        existing = dict(cur.fetchall())
        for part in parts:
            partition_id = int(part["id"])
            if partition_id in existing:
                if existing[partition_id] != part["map"]:
                    print(
                        "partition %d is %s in the database but %s in the template; left as it is"
                        % (partition_id, existing[partition_id], part["map"])
                    )
                continue
            definition = {
                "type": "box2d_array",
                "box": {
                    "min_x": number(part.get("minX"), 0),
                    "min_y": number(part.get("minY"), 0),
                    "max_x": number(part.get("maxX"), 1),
                    "max_y": number(part.get("maxY"), 1),
                },
            }
            cur.execute(
                "INSERT INTO world_partition"
                " (partition_id, map, partition_definition, dimension_index, blocked)"
                " VALUES (%s, %s, %s::jsonb, %s, %s)"
                " ON CONFLICT (partition_id) DO NOTHING",
                (
                    partition_id,
                    part["map"],
                    json.dumps(definition, separators=(",", ":")),
                    int(part.get("dimension") or 0),
                    part.get("disable", "false").lower() == "true",
                ),
            )
            added += cur.rowcount
        cur.execute(
            "SELECT setval(pg_get_serial_sequence('world_partition', 'partition_id'),"
            " GREATEST((SELECT max(partition_id) FROM world_partition), 1))"
        )
        cur.execute("SELECT update_partition_labels(false)")
    conn.close()
    print("world partitions: %d in the template, %d added" % (len(parts), added))


if __name__ == "__main__":
    main()
