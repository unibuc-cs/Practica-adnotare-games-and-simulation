# Battlefield 6 — Gameplay Action Annotation

## Goal
Create a compact dataset from **YouTube Battlefield 6 gameplay** for training **action recognition** with VLMs.

---

## What you must submit (per student)
1) **`annotations.jsonl`** — at least **40 JSONL entries/lines** (one labeled moment per line)  
2) **`clips/`** — one extracted clip per entry, named exactly by `qid`: `clips/<qid>.mp4`  
3) One ZIP named **`YourFullName_BF6.zip`** containing (1) and (2)

Start here:
- **A) Create `annotations.jsonl`** → see **Output format (JSONL)** below  
- **B) Extract clips** using the provided script → see **Clip extraction** below  

---

## What you must do (per student)
- Label **at least 40 moments** from YouTube Battlefield 6 gameplay.
- Use **gameplay only** (HUD ok). **No menus / spawn screen / scoreboard / loading** inside labeled windows.
- Avoid duplicate sources using the shared sheet.
- If more than 3 students use the same video, choose another one.

### Diversity requirement
- At least **one** example for each `scene`
- At least **two** examples for each `action`

---

## Labels

### `scene` (choose exactly one)
- `BF6_onfoot_outdoor`
- `BF6_onfoot_indoor`
- `BF6_ground_vehicle`
- `BF6_air_vehicle`
- `BF6_water_vehicle`

### `action` (choose exactly one)
- `MOVE`
- `SHOOT`
- `MELEE`
- `TAKE_COVER`
- `STUNT`
- `CRASH`
- `TAKEOFF_LAND`
- `EVADE_ENEMY`
- `WATER_TRAVEL`

---

## Output format (JSONL)

Required fields per line:
- `qid`
- `youtube_url`
- `t_start`
- `t_end`
- `scene`
- `action`
- `query` (≥ 8 words, full sentence, ends with a period)

---

## Timing rules
- Use seconds from YouTube timeline.
- Recommended duration: **3–10 seconds**
- Allowed range: **2–15 seconds**
- `EVADE_ENEMY` may be **5–20 seconds**.

---

## Clip extraction

Install:
```powershell
winget install Gyan.FFmpeg
winget install OpenJS.NodeJS.LTS
pip install -U yt-dlp
```

Run:
```powershell
python extract_clips_strict.py --jsonl annotations.jsonl
```

---

## Example JSONL entries
```json
{"qid":"student_0","youtube_url":"https://youtu.be/EXAMPLE1","t_start":120,"t_end":128,"scene":"BF6_onfoot_outdoor","action":"SHOOT","query":"The player fires repeatedly at enemies across an open battlefield."}
{"qid":"student_1","youtube_url":"https://youtu.be/EXAMPLE2","t_start":300,"t_end":308,"scene":"BF6_air_vehicle","action":"TAKEOFF_LAND","query":"The jet accelerates and lifts off from the runway."}
```

---

## Quick checklist
- Unique `qid`
- Tight time window
- No menus inside window
- One dominant action
- Proper full-sentence query
