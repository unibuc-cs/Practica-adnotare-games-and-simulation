# GTA V — Gameplay Action Annotation

## Goal
Create a compact dataset from **YouTube GTA V gameplay** for training **action recognition** with VLMs.

---

## What you must submit (per student)
1) **`annotations.jsonl`** — at least **40 JSONL entries/lines** (one labeled moment per line)  
2) **`clips/`** — one extracted clip per entry, named exactly by `qid`: `clips/<qid>.mp4`  
3) One ZIP named **`YourFullName_GTA5.zip`** containing (1) and (2)

Start here:
- **A) Create `annotations.jsonl`** → see **Output format (JSONL)** below  
- **B) Extract clips** using the provided script → see **Clip extraction** below


---


## What you must do (per student)
- Label **at least 40 moments** (**40 JSONL entries/lines**) from YouTube GTA V gameplay (40 labeled windows, not necessarily 40 different videos).
- Use **gameplay only** (HUD ok). **No menus / map / pause / settings / loading** inside labeled windows.
- Avoid duplicate sources: before using a YouTube video, check **VideosUsed.xls** (shared sheet). Then add your name and link there.

- **NOTE**: If you see that the link is used more than 3 people, find another one.


**Recommendation:** for each labeled moment, make sure there is **clean gameplay** around it (no menus) and avoid moments that are heavily edited with rapid cuts.  
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
- `GTA5_onfoot_outdoor`
- `GTA5_onfoot_indoor`
- `GTA5_driving`
- `GTA5_flying`
- `GTA5_water`

### `action` (behavior only; no overlap with scene)
Choose exactly one:
- `MOVE` (movement is the main thing; valid in any `scene` when no more specific action label fits)
- `SHOOT` (visible firing is the main thing)
- `MELEE` (punch/kick/melee hits)
- `TAKE_COVER` (entering/using cover dominates)
- `STUNT` (jump/ramp/drift/extreme maneuver dominates)
- `CRASH` (collision dominates)
- `TAKEOFF_LAND` (takeoff or landing dominates; aircraft)
- `EVADE_POLICE` (escaping while wanted stars are visible)
- `WATER_TRAVEL` (swim/boat travel dominates)

**Quick disambiguation**
- Swimming/boating → `WATER_TRAVEL` (not `MOVE`)
- Takeoff/landing → `TAKEOFF_LAND` (not `MOVE`)
- Clear collision → `CRASH` even if driving continues afterward

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
Your `[t_start, t_end]` must be **tight**:
- `t_start`: the first second when the target action clearly begins
- `t_end`: the last second when the target action is still happening
- If two actions overlap, choose the dominant one or split into two separate entries.

### Duration
Keep each labeled moment short and focused:
- **Recommended duration:** **3–10 seconds**
- **Allowed range:** **2–15 seconds**
- If you need longer than 15 seconds, you should usually **split** into multiple entries.

**Exception:** `EVADE_POLICE` can be slightly longer (sustained behavior):
- **Recommended:** **5–20 seconds** (still tight boundaries, no extra padding)


---

## Clip extraction (generate `clips/<qid>.mp4`)
After you create `annotations.jsonl`, extract each labeled moment as a local video clip named by `qid`:

- Output folder: `clips/`
- File naming: `clips/<qid>.mp4` (one clip per JSONL line)
- Clip content: exactly the moment `[t_start, t_end]` (YouTube timeline)

### Install prerequisites (Windows / macOS / Linux)
You need:
- **Python 3.10+**
- **yt-dlp**
- **ffmpeg**
- **Node.js (LTS)** (required by yt-dlp for reliable YouTube extraction)

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

### Run the provided extractor script
This repository includes a script (for example `extract_clips_strict.py`) that:
1) downloads each YouTube video **once** into `cache/`  
2) cuts each `[t_start, t_end]` moment into `clips/<qid>.mp4`

Run from the repo folder:
```powershell
python extract_clips_strict.py --jsonl annotations.jsonl
```

### If you get YouTube warnings / 403 errors
The extractor should use:
- browser cookies (Chrome or Edge)  
- Node.js runtime  
- Android player client (more reliable)

If you need to run yt-dlp manually for debugging, use:
```powershell
yt-dlp --no-playlist --cookies-from-browser chrome --js-runtimes node --extractor-args "youtube:player_client=android" -f "bv*+ba/best" --merge-output-format mp4 -o "cache/%(id)s.%(ext)s" "<YOUTUBE_URL>"
```
(Replace `chrome` with `edge` if you use Edge.)

---


## Examples (students must replace the URL, times,scene, action, query)
```json
{"qid":"ciprian_paduraru_00","youtube_url":"https://youtu.be/X9zKVbvGfeY","t_start":738,"t_end":753,"scene":"GTA5_onfoot_outdoor","action":"MOVE","query":"MOVE: The player runs through snow to reach a graveyard."}
{"qid":"ciprian_paduraru_01","youtube_url":"https://youtu.be/X9zKVbvGfeY","t_start":646,"t_end":657,"scene":"GTA5_driving","action":"MOVE","query":"MOVE: The car moves quickly on snow and icy roads."}
{"qid":"ciprian_paduraru_02","youtube_url":"https://youtu.be/X9zKVbvGfeY","t_start":1296,"t_end":1304,"scene":"GTA5_flying","action":"TAKEOFF_LAND","query":"TAKEOFF_LAND: The aircraft attempts a landing at a small airfield."}
{"qid":"ciprian_paduraru_03","youtube_url":"https://youtu.be/5CG_qMwTB3M","t_start":22,"t_end":32,"scene":"GTA5_onfoot_outdoor","action":"SHOOT","query":"SHOOT: The player fires at NPCs inside a restaurant."}
{"qid":"ciprian_paduraru_04","youtube_url":"https://youtu.be/5CG_qMwTB3M","t_start":479,"t_end":489,"scene":"GTA5_flying","action":"MOVE","query":"MOVE: The jet flies over mountains at high altitude."}
{"qid":"ciprian_paduraru_05","youtube_url":"https://youtu.be/TgmCyxevAs4","t_start":147,"t_end":154,"scene":"GTA5_driving","action":"EVADE_POLICE","query":"EVADE_POLICE: The player speeds away while a police car follows."}

```



## What to submit
Upload one ZIP named **`YourFullName_GTA5.zip`** containing:
- `annotations.jsonl`
- `clips/` with one file per entry: `clips/<qid>.mp4`


## Quick checklist (before submitting)
- `qid` is unique and filename-safe (letters/numbers/underscore)
- Window is **tight** (≤ 1s padding each side) and duration is within the guideline
- No menus inside `[t_start, t_end]`
- One dominant action per line
- `query` is a full sentence (≥ 8 words, ends with a period)
