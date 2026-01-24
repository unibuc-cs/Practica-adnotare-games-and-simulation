import argparse
import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse, parse_qs

# -----------------------------
# Config: labels + constraints
# -----------------------------
SCENES = {
    "GTA5_onfoot_outdoor",
    "GTA5_onfoot_indoor",
    "GTA5_driving",
    "GTA5_flying",
    "GTA5_water",
    "GTA5_cinematic_cam",
}

ACTIONS = {
    "MOVE",
    "SHOOT",
    "MELEE",
    "TAKE_COVER",
    "STUNT",
    "CRASH",
    "TAKEOFF_LAND",
    "EVADE_POLICE",
    "WATER_TRAVEL",
}

# Duration rules (seconds)
REC_MIN, REC_MAX = 3, 10
ALLOWED_MIN, ALLOWED_MAX = 2, 15
EVADE_REC_MIN, EVADE_REC_MAX = 5, 20
EVADE_ALLOWED_MIN, EVADE_ALLOWED_MAX = 2, 25  # slightly lenient upper bound

QID_SAFE = re.compile(r"^[A-Za-z0-9_\-]+$")


@dataclass
class Issue:
    level: str  # "ERROR" or "WARN"
    msg: str


def run(cmd: list[str]) -> None:
    print(">", " ".join(cmd))
    subprocess.run(cmd, check=True)


def youtube_id_from_url(url: str) -> str | None:
    u = urlparse(url)
    host = (u.netloc or "").lower()
    if host.endswith("youtu.be"):
        vid = u.path.strip("/").split("/")[0]
        return vid or None
    if "youtube.com" in host:
        qs = parse_qs(u.query)
        return qs.get("v", [None])[0]
    return None


def sanitize_qid(qid: str) -> str:
    # convert spaces/diacritics to underscore-like safe form
    return re.sub(r"[^A-Za-z0-9_\-]+", "_", qid).strip("_")


def word_count(s: str) -> int:
    # counts word-ish tokens
    return len([w for w in re.split(r"\s+", s.strip()) if w])


def is_full_sentence(s: str) -> bool:
    s = s.strip()
    return bool(s) and s[0].isupper() and s.endswith(".")


def validate_entry(e: dict, line_no: int) -> tuple[dict, list[Issue]]:
    issues: list[Issue] = []

    # Required fields
    for k in ["qid", "youtube_url", "t_start", "t_end", "scene", "action", "query"]:
        if k not in e:
            issues.append(Issue("ERROR", f"Line {line_no}: missing required field '{k}'"))
            return e, issues  # can't continue

    # qid
    qid_raw = e["qid"]
    if not isinstance(qid_raw, str):
        issues.append(Issue("ERROR", f"Line {line_no}: qid must be a string, got {type(qid_raw).__name__}"))
        return e, issues
    qid = sanitize_qid(qid_raw)
    if qid != qid_raw:
        issues.append(Issue("WARN", f"Line {line_no}: qid '{qid_raw}' contains unsafe chars; will use '{qid}'"))
    if not qid or not QID_SAFE.match(qid):
        issues.append(Issue("ERROR", f"Line {line_no}: qid '{qid}' is not filename-safe (use A-Z a-z 0-9 _ -)"))
    e["qid"] = qid

    # url
    url = e["youtube_url"]
    if not isinstance(url, str) or not url.strip():
        issues.append(Issue("ERROR", f"Line {line_no}: youtube_url must be a non-empty string"))
        return e, issues
    vid = youtube_id_from_url(url.strip())
    if not vid:
        issues.append(Issue("ERROR", f"Line {line_no}: youtube_url is not a recognized YouTube watch URL: {url}"))
        return e, issues
    e["_youtube_id"] = vid

    # scene/action labels
    scene = e["scene"]
    action = e["action"]
    if scene not in SCENES:
        issues.append(Issue("ERROR", f"Line {line_no}: scene '{scene}' not in allowed set {sorted(SCENES)}"))
    if action not in ACTIONS:
        issues.append(Issue("ERROR", f"Line {line_no}: action '{action}' not in allowed set {sorted(ACTIONS)}"))

    # timing
    try:
        ts = float(e["t_start"])
        te = float(e["t_end"])
    except Exception:
        issues.append(Issue("ERROR", f"Line {line_no}: t_start/t_end must be numbers (seconds)"))
        return e, issues

    if ts.is_integer() is False or te.is_integer() is False:
        issues.append(Issue("WARN", f"Line {line_no}: t_start/t_end are not integers; will round to nearest second"))
    t_start = int(round(ts))
    t_end = int(round(te))

    if t_start < 0 or t_end < 0:
        issues.append(Issue("ERROR", f"Line {line_no}: times must be >= 0 (got {t_start}, {t_end})"))
    if t_start >= t_end:
        issues.append(Issue("ERROR", f"Line {line_no}: require t_start < t_end (got {t_start}, {t_end})"))

    e["t_start"] = t_start
    e["t_end"] = t_end

    # duration rules
    dur = t_end - t_start
    if dur <= 0:
        issues.append(Issue("ERROR", f"Line {line_no}: non-positive duration after rounding: {dur}s"))
    else:
        if action == "EVADE_POLICE":
            if not (EVADE_ALLOWED_MIN <= dur <= EVADE_ALLOWED_MAX):
                issues.append(Issue("WARN", f"Line {line_no}: EVADE_POLICE duration {dur}s outside allowed {EVADE_ALLOWED_MIN}-{EVADE_ALLOWED_MAX}s"))
            elif not (EVADE_REC_MIN <= dur <= EVADE_REC_MAX):
                issues.append(Issue("WARN", f"Line {line_no}: EVADE_POLICE duration {dur}s outside recommended {EVADE_REC_MIN}-{EVADE_REC_MAX}s"))
        else:
            if not (ALLOWED_MIN <= dur <= ALLOWED_MAX):
                issues.append(Issue("WARN", f"Line {line_no}: duration {dur}s outside allowed {ALLOWED_MIN}-{ALLOWED_MAX}s"))
            elif not (REC_MIN <= dur <= REC_MAX):
                issues.append(Issue("WARN", f"Line {line_no}: duration {dur}s outside recommended {REC_MIN}-{REC_MAX}s"))

    # query rules
    q = e["query"]
    if not isinstance(q, str) or not q.strip():
        issues.append(Issue("ERROR", f"Line {line_no}: query must be a non-empty string"))
    else:
        q = q.strip()
        # Must start with ACTION:
        if not q.startswith(f"{action}:"):
            issues.append(Issue("WARN", f"Line {line_no}: query should start with '{action}:'"))
        # full sentence + word count
        if not is_full_sentence(q):
            issues.append(Issue("WARN", f"Line {line_no}: query should be a full sentence (Capitalized, ends with '.')"))
        if word_count(q) < 8:
            issues.append(Issue("WARN", f"Line {line_no}: query has < 8 words"))

        e["query"] = q

    return e, issues


def download_to_cache(youtube_url: str, vid: str, cache_dir: Path) -> Path:
    outtmpl = str(cache_dir / f"{vid}.%(ext)s")
    run([
        "yt-dlp",
        "--no-playlist",
        "-f", "bv*+ba/best",
        "--merge-output-format", "mp4",
        "-o", outtmpl,
        youtube_url
    ])
    candidates = sorted(cache_dir.glob(f"{vid}.*"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not candidates:
        raise FileNotFoundError(f"Download failed: no cached file for video id {vid}")
    return candidates[0]


def cut_clip(src_path: Path, out_path: Path, t_start: int, t_end: int, overwrite: bool) -> None:
    if out_path.exists() and not overwrite:
        return  # caller handles messaging
    run([
        "ffmpeg",
        "-hide_banner", "-loglevel", "error",
        "-i", str(src_path),
        "-ss", str(t_start),
        "-to", str(t_end),
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "23",
        "-c:a", "aac",
        "-y" if overwrite else "-n",
        str(out_path)
    ])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jsonl", default="annotations.jsonl", help="Path to JSONL file")
    ap.add_argument("--cache", default="cache", help="Cache folder for downloaded sources")
    ap.add_argument("--clips", default="clips", help="Output folder for clips")
    ap.add_argument("--overwrite", action="store_true", help="Overwrite existing clips")
    ap.add_argument("--fail_on_warn", action="store_true", help="Treat warnings as errors")
    args = ap.parse_args()

    jsonl_path = Path(args.jsonl)
    cache_dir = Path(args.cache)
    clips_dir = Path(args.clips)
    cache_dir.mkdir(exist_ok=True)
    clips_dir.mkdir(exist_ok=True)

    # Load + validate
    entries: list[dict] = []
    all_issues: list[Issue] = []
    seen_qid: set[str] = set()

    with jsonl_path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                e = json.loads(line)
            except json.JSONDecodeError as ex:
                all_issues.append(Issue("ERROR", f"Line {line_no}: invalid JSON ({ex})"))
                continue

            e, issues = validate_entry(e, line_no)
            all_issues.extend(issues)

            if any(i.level == "ERROR" for i in issues):
                continue

            # qid uniqueness
            qid = e["qid"]
            if qid in seen_qid:
                all_issues.append(Issue("ERROR", f"Line {line_no}: duplicate qid '{qid}'"))
                continue
            seen_qid.add(qid)

            entries.append(e)

    # Print issues
    errors = [i for i in all_issues if i.level == "ERROR"]
    warns = [i for i in all_issues if i.level == "WARN"]
    for i in all_issues:
        print(f"{i.level}: {i.msg}")

    if errors or (args.fail_on_warn and warns):
        raise SystemExit(f"Validation failed: {len(errors)} errors, {len(warns)} warnings")

    # Download cache per YouTube id
    cache_map: dict[str, Path] = {}
    for e in entries:
        vid = e["_youtube_id"]
        url = e["youtube_url"]
        if vid not in cache_map:
            cached = next(iter(sorted(cache_dir.glob(f"{vid}.*"))), None)
            if cached and cached.exists():
                cache_map[vid] = cached
            else:
                cache_map[vid] = download_to_cache(url, vid, cache_dir)

    # Cut clips
    created = 0
    skipped = 0
    for e in entries:
        qid = e["qid"]
        vid = e["_youtube_id"]
        out_path = clips_dir / f"{qid}.mp4"

        if out_path.exists() and not args.overwrite:
            print(f"SKIP: {qid} (clip exists: {out_path})")
            skipped += 1
            continue

        cut_clip(cache_map[vid], out_path, e["t_start"], e["t_end"], overwrite=True)
        print(f"OK: {qid} -> {out_path}")
        created += 1

    print(f"Done. Created={created}, Skipped={skipped}, Output={clips_dir.resolve()}")


if __name__ == "__main__":
    main()
