#!/usr/bin/env python3
"""Match WhatsApp vocales to screenshot timestamps by duration, then rename."""
import os
import re
import struct

FOLDER = os.path.join(os.path.dirname(__file__), "487_vocales")
TOLERANCE = 3.0

# June 12 call recordings from screenshots (487 taxi day)
REFERENCE = [
    ("2026-06-12", "17:38", 168),
    ("2026-06-12", "17:48", 83),
    ("2026-06-12", "17:57", 281),
    ("2026-06-12", "18:04", 438),
    ("2026-06-12", "18:14", 317),
    ("2026-06-12", "18:20", 342),
    ("2026-06-12", "18:28", 287),
    ("2026-06-12", "18:34", 163),
    ("2026-06-12", "18:38", 377),
    ("2026-06-12", "18:46", 40),
    ("2026-06-12", "18:47", 533),
    ("2026-06-12", "19:00", 417),
    ("2026-06-12", "19:12", 27),
    ("2026-06-12", "19:15", 7),
    ("2026-06-12", "19:15", 65),
    ("2026-06-12", "19:40", 76),
    ("2026-06-12", "19:43", 110),
    ("2026-06-12", "19:53", 286),
    ("2026-06-12", "20:00", 4),
    ("2026-06-12", "20:07", 44),
    ("2026-06-12", "20:26", 28),
    ("2026-06-12", "20:36", 25),
    ("2026-06-12", "20:45", 39),
]


def get_duration(path):
    with open(path, "rb") as f:
        data = f.read()
    pos = 0
    while True:
        pos = data.find(b"mvhd", pos)
        if pos < 0:
            return None
        mvhd = data[pos + 4 : pos + 104]
        if len(mvhd) < 20:
            pos += 4
            continue
        ver = mvhd[0]
        if ver == 0:
            timescale = struct.unpack(">I", mvhd[12:16])[0]
            duration = struct.unpack(">I", mvhd[16:20])[0]
        else:
            timescale = struct.unpack(">I", mvhd[20:24])[0]
            duration = struct.unpack(">Q", mvhd[24:32])[0]
        if timescale > 0 and duration > 0:
            return duration / timescale
        pos += 4
    return None


def fmt_dur(sec):
    sec = int(round(sec))
    return f"{sec // 60:02d}m{sec % 60:02d}s"


def safe_name(date, time_str, dur_sec, suffix=""):
    t = time_str.replace(":", "-")
    return re.sub(r'[<>:"/\\|?*]', "-", f"{date}_{t}_{fmt_dur(dur_sec)}{suffix}.mp4")


def match_all(refs, files):
    refs = [{"date": d, "time": t, "sec": s, "id": i} for i, (d, t, s) in enumerate(refs)]
    pairs = []
    for f in files:
        for r in refs:
            diff = abs(r["sec"] - f["dur"])
            if diff <= TOLERANCE:
                pairs.append((diff, f["name"], f, r))
    pairs.sort(key=lambda x: (x[0], x[1]))

    used_files, used_ref_ids = set(), set()
    assignments = []
    for diff, _, f, r in pairs:
        if f["name"] in used_files or r["id"] in used_ref_ids:
            continue
        used_files.add(f["name"])
        used_ref_ids.add(r["id"])
        assignments.append((f, r, diff))

    # Duplicates: same recording exported twice (168s x2, 342s x2)
    rest = [f for f in files if f["name"] not in used_files]
    for f in rest:
        best = min(refs, key=lambda r: abs(r["sec"] - f["dur"]))
        if abs(best["sec"] - f["dur"]) <= TOLERANCE:
            dup = dict(best)
            dup["dup"] = True
            assignments.append((f, dup, abs(best["sec"] - f["dur"])))

    return assignments


def main(dry_run=True):
    files = []
    for name in sorted(os.listdir(FOLDER)):
        if not name.lower().endswith(".mp4"):
            continue
        path = os.path.join(FOLDER, name)
        dur = get_duration(path)
        if dur is None:
            print(f"SKIP: {name}")
            continue
        files.append({"name": name, "path": path, "dur": dur})

    assignments = match_all(REFERENCE, files)
    assignments.sort(key=lambda a: (a[1]["date"], a[1]["time"], a[0]["name"]))

    print("=" * 92)
    print(f"{'ORIGINAL':<50} {'SEC':>5}  {'diff':>4}  NEW NAME")
    print("=" * 92)

    renames = []
    used_names = set()
    dup_count = {}

    for f, r, diff in assignments:
        key = (r["date"], r["time"])
        suffix = ""
        if r.get("dup"):
            dup_count[key] = dup_count.get(key, 0) + 1
            suffix = f"_v{dup_count[key] + 1}"
        new_name = safe_name(r["date"], r["time"], f["dur"], suffix)
        if new_name in used_names:
            n = 2
            while safe_name(r["date"], r["time"], f["dur"], f"_v{n}") in used_names:
                n += 1
            new_name = safe_name(r["date"], r["time"], f["dur"], f"_v{n}")
        used_names.add(new_name)
        renames.append((f["path"], os.path.join(FOLDER, new_name)))
        print(f"{f['name'][:50]:<50} {f['dur']:5.0f}  {diff:4.1f}  {new_name}")

    matched = {a[0]["name"] for a in assignments}
    if len(matched) != len(files):
        print("\nUNMATCHED:")
        for f in files:
            if f["name"] not in matched:
                print(f"  {f['name']} ({f['dur']:.1f}s)")

    if dry_run:
        print(f"\n[DRY RUN] {len(renames)}/{len(files)} matched. Run: python rename_vocales.py --apply")
        return

    for old, new in renames:
        if os.path.abspath(old) == os.path.abspath(new):
            continue
        if os.path.exists(new):
            raise SystemExit(f"Exists: {new}")
        os.rename(old, new)
    print(f"\nRenamed {len(renames)} files in {FOLDER}")


if __name__ == "__main__":
    import sys
    main("--apply" not in sys.argv)
