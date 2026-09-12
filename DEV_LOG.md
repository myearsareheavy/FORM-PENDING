# Form Pending — Development Log

## Polish pass (post-RC)

- Handler dialogue is first person (`I keep the stamp`) instead of naming themselves in third person. Referrals to other people stay third person; duplicate first names use the full name.
- First names are pooled as feminine / masculine / unisex and drive sprite presentation (hair, accessories, body silhouette).
- Visuals: corridor runner, door slabs, elevator floor lamp, desk variants, speckled carpets (no stripe weave), clearer visitor lanyard vs clerks.

## Checkpoint 4

Release candidate.

- Final regression: generate (25), notebook, loop, smoke, and `tests/test_release.py` (45 fresh seeds 5000–5039 plus five strings).
- All of those seeds solvable; efficient talk+elevator routes 32–63 sim minutes (mean 46) of a 540-minute day.
- Success, 5:00 PM failure, notebook isolation, and new-run generation verified through the Game object.
- Diagnostic log contains only `test_injected_failure` rows from unit tests — zero genuine OUT TO LUNCH from generation.
- Player README rewritten for blind play. F3 stays in code, off by default, not listed as a control. Seed remains on the HUD.
- No third-party art/audio; pygame plus system fonts.

Not live-timed in a windowed session.

## Checkpoint 3

Polish pass on comedy, navigation, pacing, and feel.

- **Dialogue:** Larger greeting/idle pools, department flavor, authored grant lines, shorter revisits. Intake has its own opening lines and stands in the lobby so the first referral actually happens.
- **Navigation:** Wall memos (flavor + truthful “X is on Floor N”), department plaques at room centers, elevator directory still the index. Some clerks mention the board by the elevator.
- **Floors:** Extra props (boxes, cabinets, chairs, plants). Memos as readable notices. Chain desks get a small red folder so the right pile is findable without looking Chosen.
- **Time:** Idle clock 6s/sim minute (~54 real min for a full idle day). Flavor talk +2, chain +3, revisit +1, elevator 1+1/floor. Perfect chain of talks leaves most of the day; wandering still costs.
- **Feel:** Walk bob, footstep ticks, paper/ding/stamp blips (procedural WAV, mute with M), elevator fade, “Received:” toast, 4:00 warning, dialogue page numbers, tighter inventory strip.
- **Catastrophes:** Three new stakes (please / pencils / clocks) plus tableaus. Event beat slightly longer.
- **Tests:** memos+intake placement, revisit length, perfect-chain time budget. 25 generation seeds still all solvable. No generation OUT TO LUNCH.

Still not live-playtested in a window. Audio is silent under the dummy driver used in tests.

## Checkpoint 2

Complete game loop is in.

- **Notebook:** Freeform only (type, delete, newlines, arrows, home/end, scroll). Open with N, close with ESC. Dialogue is never copied in. Time still passes while writing.
- **Time:** Idle clock ~5.5 real seconds per sim minute (~50 real minutes for 8–5 if you stand still). Talk +4 min, elevator 2+1/floor, reading +1. Clock freezes after a successful filing so the talk that files can beat the bell. After 4:00 the HUD goes red and a closing banner appears.
- **Success:** Stamp sequence → clerk does not look up → averted catastrophe card. ENTER starts a new random seed; ESC returns to title.
- **Failure:** 5:00 PM → CLOSED sign → black beat → catastrophe tableau (varies by run) → `FORM … WAS NOT PROCESSED`.
- **Restart:** Endings and title both generate a fresh run. Notebook clears.
- **OUT TO LUNCH:** `audit_world` + `apply_failsafe` on every start. Missing chain NPC/item marks the desk OUT TO LUNCH, logs JSONL (`seed`, NPC, expected, actual, reason, recovery), and leaves a manila envelope so the run stays completable. Authored lunch jokes are not routed through this. 25 generated seeds produced **zero** activations. One test-injected activation verified the envelope path.
- **Variation:** Seeds 1 vs 2 differ in document, catastrophe, chain, and names; endings use that run’s stakes.

Tests added: `tests/test_notebook.py`, `tests/test_loop.py` (filing, 5pm fail, notebook isolation, lunch envelope, restart, ending draw).

Known remaining: first-time run length not measured in a live window; catastrophe tableaus are short stills not animations; floors still sparse; no audio; clock balance is a first pass.

## Checkpoint 1

### Architecture

- **Stack:** Python 3 + pygame. Chosen because Node.js is not present in this environment and pygame already is. Single language for generation, validation, and the playable client. No asset pipeline.
- **View:** Top-down 2D office, camera follows the player. Not pixel art.
- **Visual direction:** Municipal modernist — manila/paper UI, rubber-stamp red, IBM-ish type, color-coded floors (intake beige, records teal, permits mustard, personnel rose, compliance navy, executive walnut). NPCs are geometric figures with hair/shirt/accessory combinations. Furniture is drawn procedurally.
- **Controls:** WASD/arrows, E to interact, numbered elevator, R to read the starting document.

### Procedural generation

Generation is **structurally valid by construction**, then validated.

1. Seed → Mulberry32 RNG with forkable streams (`floorN`, `npcs`, `chain`, `talk`).
2. Assign departments to floors (mostly home floors, 1–3 neighbor swaps).
3. Build each floor as corridor-spine + rooms + desks. Elevator cabin is identical on every floor.
4. Place NPCs only at desks whose standing tile is flood-fill reachable from the elevator.
5. Build the bureaucratic chain **backwards from FILE** using existing NPCs, preferring matching departments and spreading across floors.
6. Assign knowledge that refers only to real NPCs/floors/departments. Intake on floor 1 always points at the first working link and truthfully refuses to file this form type.
7. Validate. On failure, retry with a derived stream; the public seed does not change. After 12 failures the world is flagged `generation_failed` and a diagnostic record is prepared (`diagnostics/out_to_lunch.jsonl`).

Chain node types: file, stamp, issue, sign, copy, correct, verify, notary, approve, prior.

### Seeds

`normalize_seed` accepts an int or string. The HUD shows the numeric seed. `py -3 main.py 42` reproduces a run. Same seed has been verified to produce identical names, chain, and document codes.

### Validation

`validate_world` checks: six floors, NPC uniqueness, FILE root, DAG acyclicity, item producers, referral facts vs living NPCs, elevator presence, chain-NPC reachability, and a perfect-player `simulate_completion` walk.

### Tests (CP1)

- 25 seeds (numeric and string): all generated valid, all solvable, no `generation_failed`.
- Same seed is deterministic.
- Distinct seeds differ in chain/names/document/catastrophe (>90% of pairs).
- Talk resolution: leaf-to-root grants succeed; filing without prerequisites is refused.
- Headless pygame smoke: launch, draw all six floors, overlays, elevator travel, wall collision.

### Known issues / not yet in

- Manual notebook is not in this checkpoint (title screen says so).
- 5:00 PM currently shows a notice card, not a full catastrophe cinematic.
- Successful filing is implemented as a notice, not a polished ending.
- Clock rate is a first pass (~6 real seconds per simulated minute).
- Floors are readable but still sparse; more props, waiting areas, and signage belong in polish.
- No audio.
- NPC pathfinding/idle animation none — they sit at desks, which is correct for clerks.
- Department plaques sometimes sit in corners; directories near the elevator are the reliable map.
- Dummy-driver screenshots were used for visual checks; a windowed play session was not observed on a physical display in this environment.

### Next (Checkpoint 2)

- Freeform notebook (no auto quest log).
- Tune time costs (walking already ticks; talks and elevator already cost minutes).
- Full 5:00 PM failure cinematic using the run's catastrophe.
- Polish filing success.
- More dialogue variety and incidental signage.
- OUT TO LUNCH runtime fail-safe wired to actual invalid NPC/dependency cases (generation path already logs).
- Ensure two fresh runs feel observably different in play, not only in data.
