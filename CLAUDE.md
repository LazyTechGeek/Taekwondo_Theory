# ITF Taekwondo Theory — project notes

Dave's (Taekwondo instructor, UK, UKTC) mobile-first theory app for his students, many of them children.
Live on GitHub Pages from this repo. Read this file first; keep it short and update it when a rule or decision changes.

## Files
- `index.html` — the whole app (single file, ~1.3 MB, vanilla JS). Edit it in place with small targeted replacements; never regenerate it.
- `all-theory.xlsx` — Dave's master "All Theory" workbook: the single source of truth for all content.
- `pattern-exam.html` + `videos/` — separate Pattern Exam test page (video pauses, "What's next?" questions), built in another chat; not linked from the app yet.
- `mp3/` — audio files named in the workbook's MP3 columns (file name only, lower case, e.g. `chon-ji.mp3`).
- `tools/wb2json.py` — reads and validates the workbook (IDs, grades, headers, video links/times) and prints problems.
- `tools/apply_wb.py all-theory.xlsx` — embeds the workbook data (`<script id="allTheory">`) and the workbook itself (`<script id="wbTemplate">`, used by developer-mode Export) into `index.html`.
- `tools/check.py` — node syntax check + Playwright smoke test at 390×844 and 360×640 (opens every menu item, reports errors / overflow).

## Workflow
1. Dave sends a workbook or describes a change. If he says "don't change anything / just a question", answer only.
2. For content: save his file as `all-theory.xlsx`, run `tools/apply_wb.py`, report what changed (diff old vs new data) and any problems.
3. Every change: bump `APP_VERSION` and add a line to the top of `VERSION_NOTES` (both near the end of the main script).
4. Run `tools/check.py`; screenshot anything visual at phone size.
5. **Upload (commit + push to `main`) only when Dave says so.** Commit as LazyTechGeek.
6. Replies: short and plain English; he often asks for the request to be repeated back before building.

## Workbook (tabs: Terminology, Patterns, Belt meanings, Questions, How to fill in)
- Grade column `10th_Kup`…`1st_Kup`, `1st_Dan`…`5th_Dan` (Questions may use `All`). Belt: White, Yellow tag … Black (all Dan grades = Black).
- IDs: `T_10th-Kup_01`, `P_1st-Dan_3`, `B_White`, `Q_10th-Kup_01`, `Q_All_01`. Never reuse or renumber an ID; a new row takes the next unused number; a wording fix keeps its ID (audio is linked by ID).
- Yellow columns are Dave's: Pronounced / MP3 (Questions: Question pronounced, Question MP3, Answer pronounced, Answer MP3), Wrong answers, Video link, Video start/end (m:ss).
- Multiple answers / wrong answers are separated by `|`. A question's wrong answers are only ever used for that question (never borrowed).
- Watch for slips Dave has made before: a header overwritten (e.g. "Pronounced" typed over), duplicate IDs, editing an older copy.

## Standing rules
- Spellings exactly as in Dave's syllabus (only letter case is tidied for display). "Kup", not "Cup".
- Never ask which grade learns a pattern. Chon-Ji is 9th Kup. Yul-Gok has 38 moves. 3rd Dan sweeping kick = Goro chagi.
- Top grade is displayed "5th Dan +" (nothing new after 5th Dan); data still says 5th_Dan.
- No data collection, ever (children). Progress stays on the device; Export/Import game data is a file the student keeps (only `tkd_` localStorage keys; dev edits excluded).
- Pattern videos only from the two YouTube channels Dave's instructor approved; no link = no Watch button. Se-Jong and Tong-Il have none yet.
- Every game: "← Menu" button top-left. Screens should fit one phone screen. Keep the dark game styling.
- Main Settings (grade dropdown, Material; Advanced = Topics, Question direction, Backup & Restore) are global defaults. Learn and Practice items follow them (Study Guide, Flashcards and Patterns keep their own scope switch). Every Mini Game / Game Show starts from them and has its own Questions choice (My grade / Up to / All / Between grades) that never changes the globals.
- Simplified mode hides descriptions and belt names (for children); never mention children in the UI.

## Features worth knowing
- Study Guide: play buttons (MP3 → Pronounced → text as written, en-GB TTS), Play all, Hide Korean/English/answers (answers reveal silently, then ▶ / Hide), Grade questions in each grade, General Knowledge card under the last grade shown, pattern videos.
- Hidden developer mode: Version history → tap the title 5 times. Edit Pronounced/MP3 per item, Copy changes, Export spreadsheet (rewrites only those cells of the embedded workbook).
- Embedded games run in iframes from `<script type="text/plain">` blocks (`gpSrc` Grand Prix, `bpSrc` Balloon Pop, `tlSrc` Taerigi It Lucky; `</script` escaped as `<\/script`) and get questions from host functions (`GP_MAKE`, `BP_MAKE`, `TL_MAKE`/`TL_INFO`/`TL_RANGE`/`TL_MODE`).
- Question engine: `items(fn)` → `makeQ(it,n)` (termQ / patQ / beltQ / qQ). Range for games: `RG` + `inScope`.

## Parked ideas (not built)
- Whack-a-Mole: answer signs fixed on 5 holes; moles pop up randomly; whack only the right hole; a hit sign turns green (right) or red (wrong) and stays for the round.
- Theory Fighter (Street Fighter style), Dojang Dash (platformer), falling-blocks sorter. Invaders-style shooter rejected as too hard.
- Grading Simulator (separate project), listening quiz, "practise my mistakes", progress meter, certificates (must be properly earned), picture matching with Dave's own photos.

## Open data questions flagged to Dave
Choi-Jong/Choi-Yong, Yong-Gae/Yon-Gae, So San, Sam-IL/Tong-IL, Gojong/Gojung, Dollymio/Dollimyo, Twimyo/Twio chagi, waving kick Doro/Noollo, Chunbi/Chumbi/Junbi, Noolo/Noollo, Anaero/Anearo/Anuro, Taerigi/Taeregi.
