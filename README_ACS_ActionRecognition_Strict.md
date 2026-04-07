# Assassin’s Creed Shadows — Gameplay Action Annotation

## Goal
Create a compact dataset from **YouTube Assassin’s Creed Shadows gameplay** for training **action recognition** with VLMs.

---

## What you must submit (per student)
1) **`annotations.jsonl`** — at least **40 JSONL entries/lines** (one labeled moment per line)  
2) **`clips/`** — one extracted clip per entry, named exactly by `qid`: `clips/<qid>.mp4`  
3) One ZIP named **`YourFullName_ACS.zip`** containing (1) and (2)

Start here:
- **A) Create `annotations.jsonl`** → see **Output format (JSONL)** below  
- **B) Extract clips** using the provided script → see **Clip extraction** below  

### Check the example in `StudentExample_ACS` to see a full run + script to be used.
---

## What you must do (per student)
- Label **at least 40 moments** (**40 JSONL entries/lines**) from YouTube Assassin’s Creed Shadows gameplay (40 labeled windows, not necessarily 40 different videos).
- Use **gameplay only** (HUD ok). **No menus / map / inventory / pause / settings / loading** inside labeled windows.
- Avoid duplicate sources: before using a YouTube video, check **VideosUsed.xls** (shared sheet). Then add your name and link there.

- **NOTE**: If you see that the link is used more than 3 people, find another one.

**Recommendation:** for each labeled moment, make sure there is **clean gameplay** around it (no menus) and avoid heavily edited moments with rapid cuts.  
You may label **multiple moments** from the same video, but you still submit **one JSONL line per moment**.

### Diversity requirement
- At least **one** example for each core `scene` (below)
- At least **two** examples for each `action` label (below)

---

## Labels
Each **labeled moment** must have:
- one `scene` (context)
- one `action` (behavior)

### `scene` (context / viewpoint only)
Choose exactly one:
- `ACS_outdoor_city`
- `ACS_outdoor_nature`
- `ACS_indoor`
- `ACS_stealth_area`
- `ACS_horse_travel`

### `action` (behavior only; no overlap with scene)
Choose exactly one:
- `MOVE` (movement dominates when no more specific label fits)
- `STEALTH` (sneaking/hiding dominates)
- `ASSASSINATE` (stealth kill or execution dominates)
- `MELEE` (open combat sword/spear fighting dominates)
- `RANGED_ATTACK` (bow or ranged weapon dominates)
- `TAKE_COVER` (clearly using cover dominates)
- `HORSE_TRAVEL` (horse riding dominates)
- `PARKOUR` (climbing, rooftop traversal dominates)

**Quick disambiguation**
- Rooftop jumping → `PARKOUR` (not `MOVE`)
- Riding a horse → `HORSE_TRAVEL` (not `MOVE`)
- Hidden blade kill → `ASSASSINATE` (not `MELEE`)
- Bow shot → `RANGED_ATTACK` (not `MELEE`)

---

## Output format (JSONL)
**One line = one labeled moment (one window).**

### Required fields
- `qid` : `"YourFullName_{index}"` where index starts at 0 and increments by 1 for each JSONL line (e.g., `ciprian_paduraru_0`). Use only letters/numbers/underscore.
- `youtube_url` : link
- `t_start` : start time in seconds (**YouTube timeline**)
- `t_end` : end time in seconds (**YouTube timeline**)
- `scene` : one scene label
- `action` : one action label
- `query` : a complete sentence (capitalized, ends with a period) with **at least 8 words**

> **Required labels:** `scene`, `action`. **Also required:** `query` (short full sentence, ≥ 8 words).

---

## Moments - Timing (YouTube timeline; easiest method)
`t_start` and `t_end` are in **seconds from the start of the YouTube video** (not milliseconds).

**Method (recommended):**
1) Pause at the **start** of the action  
2) Right-click the video → **Copy video URL at current time**  
3) Paste the URL and read the `t=...s` value → this is `t_start`  
4) Repeat at the **end** of the action → `t_end`  

- Example: URL ends with `&t=135s` → `t_start = 135`.

---

## Moments - Window quality (very important)

Your `[t_start, t_end]` must be **tight** and each window must be **short and focused**.

### Tight boundaries
- `t_start`: the first second when the target action clearly begins
- `t_end`: the last second when the target action is still happening
- If two actions overlap, choose the dominant one or split into two entries.

### Duration
Keep each labeled moment short and focused:
- **Recommended duration:** **3–10 seconds**
- **Allowed range:** **2–15 seconds**
- If longer than 15 seconds, usually **split** into multiple entries.

**Exception:** `STEALTH` or `HORSE_TRAVEL` can be slightly longer:
- **Recommended:** **5–20 seconds** (still tight boundaries, no extra padding)

---

## Clip extraction (generate `clips/<qid>.mp4`)
After you create `annotations.jsonl`, extract each labeled moment as a local video clip named by `qid`:

- Output folder: `clips/`
- File naming: `clips/<qid>.mp4`
- Clip content: exactly the moment `[t_start, t_end]`

### Install prerequisites (Windows / macOS / Linux)
You need:
- **Python 3.10+**
- **yt-dlp**
- **ffmpeg**
- **Node.js (LTS)**

**Windows (recommended with winget):**
```powershell
winget install Gyan.FFmpeg
winget install OpenJS.NodeJS.LTS
pip install -U yt-dlp
```

Verify:
```powershell
ffmpeg -version
yt-dlp --version
node -v
```

---

### Run the extractor
```powershell
python extract_clips_strict.py --jsonl annotations.jsonl
```

---

## Examples (students must replace URL, times, scene, action, query)
```json
{"qid":"student_0","youtube_url":"https://youtu.be/EXAMPLE1","t_start":120,"t_end":128,"scene":"ACS_outdoor_city","action":"PARKOUR","query":"The character jumps between rooftops while climbing a tall building."}
{"qid":"student_1","youtube_url":"https://youtu.be/EXAMPLE2","t_start":300,"t_end":308,"scene":"ACS_indoor","action":"ASSASSINATE","query":"The assassin performs a stealth kill on an unaware guard."}
```

---

## What to submit
Upload one ZIP named **`YourFullName_ACS.zip`** containing:
- `annotations.jsonl`
- `clips/` with one file per entry: `clips/<qid>.mp4`

---

## Quick checklist (before submitting)
- `qid` is unique and filename-safe (letters/numbers/underscore)
- Window is **tight** and within duration guidelines
- No menus inside `[t_start, t_end]`
- One dominant action per line
- `query` is a full sentence (≥ 8 words, ends with a period)
