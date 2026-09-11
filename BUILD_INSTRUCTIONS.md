# BUILD_INSTRUCTIONS.md

# Form Pending — Autonomous Build Instructions

## Purpose

You are responsible for independently designing, implementing, testing, debugging, and polishing the game described in `FORM_PENDING_DESIGN_BIBLE.md`.

Read that file in full before beginning implementation.

The design bible defines the intended player experience and the project's non-negotiable requirements. This document defines how you should work.

The goal is a finished, playable, replayable game—not a prototype, mockup, design exercise, or partial implementation.

---

## 1. Ownership and Autonomy

You own all creative and technical decisions that are not explicitly fixed by the design bible.

Do not repeatedly ask the user to choose among reasonable implementation options.

When the design bible leaves a decision open, exercise your own judgment and proceed.

Examples of decisions you should generally make yourself include:

- engine and framework;
- programming language;
- 2D vs. 3D;
- camera and perspective;
- visual style;
- asset strategy;
- control scheme;
- project architecture;
- procedural-generation algorithms;
- exact floor layouts;
- exact NPC count;
- dialogue presentation;
- sound and music strategy;
- UI structure;
- navigation aids;
- pacing;
- typography;
- title treatment;
- comedy writing;
- save/load strategy;
- internal data formats;
- debugging tools;
- test strategy.

You may ask the user a question only if:

1. a genuine ambiguity prevents meaningful progress;
2. the ambiguity cannot reasonably be resolved from the design bible;
3. choosing arbitrarily would materially alter a non-negotiable requirement.

Preference questions are not blockers.

If several approaches are viable, choose one.

---

## 2. Read Before Building

Before changing project files:

1. Read `FORM_PENDING_DESIGN_BIBLE.md` completely.
2. Read this file completely.
3. Identify the non-negotiable requirements.
4. Form an implementation plan.
5. Begin work without requesting approval of the plan.

Do not ask the user to approve your architecture, art direction, game engine, or implementation plan before beginning.

The user wants to evaluate the decisions you make.

---

## 3. Build for the Player, Not the Specification

Do not treat the design bible as a checklist whose individual items can merely exist.

The systems must work together as a coherent game.

The player should actually experience:

- discovery;
- confusion;
- note-taking;
- navigation;
- fragmented information;
- bureaucratic dependency solving;
- time pressure;
- escalating frustration;
- comedy;
- relief or catastrophe.

A technically compliant game that is not enjoyable, legible, or meaningfully replayable is not complete.

Use the design bible's emotional target as a design constraint:

> "This should be easy."

followed by:

> "You've got to be fucking kidding me."

---

## 4. No User-Supplied Assets

Assume no art, audio, animation, UI kit, map, sprite sheet, model, texture, sound effect, or other asset will be provided by the user.

You are responsible for choosing an asset strategy.

You may:

- create assets programmatically;
- create simple original assets;
- use engine-native primitives;
- use procedural visuals;
- use appropriately licensed external resources if your environment permits it;
- combine these approaches.

If third-party resources are used, document their source and license.

Do not delay implementation while waiting for user assets.

Do not assume pixel art.

---

## 5. Scope Discipline

The project is intentionally small.

Prefer depth, coherence, and polish over feature count.

Do not expand the project into:

- a large RPG;
- a combat game;
- a sprawling narrative campaign;
- a life simulator;
- a city simulator;
- a multiplayer game;
- an elaborate crafting system;
- a giant economy;
- a procedural technology showcase with weak gameplay.

The core experience is one bureaucratic day in one six-story building.

Invest effort where it improves that experience.

---

## 6. Procedural Generation Standard

The bureaucracy generator is a critical system.

Every normal generated run must be solvable.

Generation should create meaningful variation without producing nonsense merely for variety.

The generated state should maintain internal consistency.

Examples:

- a required NPC must exist;
- a required NPC must be reachable;
- required forms must be obtainable;
- prerequisites must resolve;
- referrals must point to real people/departments;
- required locations must be accessible;
- the player must have enough time, under reasonable play, to succeed;
- circular dependency chains must not invalidate the run;
- a prerequisite must not require something that can only be acquired after completing that prerequisite;
- generated text should agree with generated state.

Prefer generation methods that make validity structurally likely rather than generating arbitrary content and hoping validation catches it.

Validation should still exist.

---

## 7. "Out to Lunch" Is a Fail-Safe, Not a Crutch

The design bible's `OUT TO LUNCH` mechanism exists to preserve immersion if procedural generation or runtime state becomes invalid.

It must not be used as a routine substitute for robust generation.

When a genuine procedural/runtime failure activates this state:

1. present an appropriate diegetic `OUT TO LUNCH` state to the player;
2. preserve the run as gracefully as reasonably possible;
3. record the underlying technical reason in a diagnostic log.

Create and maintain a machine-readable or clearly structured diagnostic record for genuine `OUT TO LUNCH` activations.

At minimum record:

- timestamp or run identifier;
- seed;
- relevant NPC or dependency;
- expected state;
- actual invalid state;
- detected failure reason;
- recovery behavior.

Normal authored jokes about lunch must not be counted as procedural-error activations.

---

## 8. Deterministic Seeds

Where practical, procedural runs should have identifiable seeds.

A seed should allow a problematic run to be reproduced for debugging.

Expose the current seed somewhere appropriate for development/testing.

The final player-facing presentation may keep seed information unobtrusive, but diagnostic tools should make it easy to recover.

---

## 9. Manual Notebook Requirement

The notebook is a player tool, not an automatic quest tracker.

It must support freeform player-entered text.

Do not automatically convert NPC dialogue into tasks, objectives, checklist entries, waypoint markers, or structured quest steps.

The player decides what matters.

You may provide normal text-editing usability, such as:

- typing;
- deletion;
- line breaks;
- scrolling;
- cursor movement;
- opening/closing the notebook.

Do not undermine the design by secretly giving the player an automated objective system elsewhere in the UI.

---

## 10. Information Integrity

NPCs may be incomplete, irritating, narrow, repetitive, vague, literal, or irrelevant.

They should not intentionally provide false factual information merely to make the game harder.

Generated dialogue must correspond to generated world state.

If an NPC says Janet is on Floor 4 near Procurement, Janet should actually be findable in the indicated area unless a clearly explained in-world state has legitimately changed.

The challenge should come from fragmented knowledge and dependencies, not arbitrary deception.

---

## 11. Time and Solvability

The day runs from 8:00 AM to 5:00 PM.

The target maximum real-world duration of a run is approximately one hour.

Tune simulated time so:

- exploration is possible;
- mistakes cost time;
- inefficient routing matters;
- players feel increasing pressure;
- success is achievable without foreknowledge;
- perfect play is not required;
- the final part of the day becomes meaningfully tense.

Do not create a game where the clock is decorative.

Do not create a game where the clock makes first-run success essentially impossible.

---

## 12. Development Logging

Maintain a concise development log in:

`DEV_LOG.md`

Update it as work progresses.

Record consequential decisions, not every trivial edit.

Useful entries include:

- major architecture choices;
- procedural-generation approach;
- visual-direction decisions;
- significant assumptions;
- major bugs discovered;
- systems added or removed;
- test results;
- known limitations;
- meaningful scope changes.

Do not rewrite the design bible to match implementation choices.

If implementation diverges from the design bible, treat that as an issue to resolve unless the relevant item was explicitly left open.

---

## 13. Testing Requirements

Test your work continuously rather than waiting until the end.

At minimum test:

### Core interaction
- game launches;
- player can navigate;
- floors are reachable;
- NPC interaction works;
- forms/items/state changes work;
- notebook accepts freeform input;
- clock progresses;
- success works;
- 5:00 PM failure works;
- restart/new run works.

### Procedural validity
Test multiple generated seeds.

Verify:

- every required dependency exists;
- the chain can be completed;
- references match the generated world;
- no required NPC is unreachable;
- no invalid cycles block completion;
- each run changes meaningfully;
- correct filing is possible before closing under reasonable play.

### Robustness
Attempt:

- repeated restarts;
- rapid interactions;
- revisiting NPCs;
- changing floors repeatedly;
- opening/closing notebook frequently;
- interacting near time transitions;
- continuing close to 5:00 PM;
- triggering success near deadline;
- starting multiple seeds.

### Presentation
Check:

- important text is readable;
- navigation is understandable;
- interactable elements are discoverable;
- NPCs can be distinguished sufficiently;
- the player understands the immediate premise;
- failure/success states are clear;
- placeholder/debug content is not leaking into normal play.

Fix significant issues you discover.

---

## 14. Checkpoint Protocol

Work autonomously between checkpoints.

Do not stop after every subsystem or ask the user for continuous guidance.

There are four required checkpoints.

When you reach a checkpoint:

1. finish the checkpoint's work to a coherent state;
2. test it;
3. update `DEV_LOG.md`;
4. provide the user a concise checkpoint report;
5. stop and wait for a response.

The user will normally respond with one of:

- `APPROVE`
- `REJECT: <one reason>`
- an answer to a question that genuinely blocked progress

Do not interpret silence or unrelated discussion as approval.

Do not proceed past a required checkpoint until approved.

---

# CHECKPOINT 1 — PLAYABLE FOUNDATION

Checkpoint 1 is reached when the project has a functioning playable foundation.

It should include, at minimum:

- a project that launches successfully;
- the chosen visual/presentation direction established enough to evaluate;
- player navigation;
- a six-floor building structure;
- movement between floors;
- NPC representation and basic interaction;
- the core data structures for documents, requirements, people, locations, and dependencies;
- an initial procedural-generation approach;
- deterministic/recoverable run seeds where practical;
- enough generated content to demonstrate the intended architecture;
- initial validation/error-handling strategy.

This checkpoint does **not** require the complete game loop.

### Checkpoint 1 report

Report:

- what is currently playable;
- major implementation decisions;
- procedural-generation architecture;
- how seeds/validation work;
- visual/presentation direction chosen;
- tests performed;
- known issues;
- what you intend to implement before Checkpoint 2.

Then stop.

---

# CHECKPOINT 2 — COMPLETE GAME LOOP

Checkpoint 2 is reached when a complete run can be played from beginning to end.

It should include:

- 8:00 AM start;
- generated filing objective;
- generated bureaucratic dependency chain;
- usable six-floor environment;
- NPC referrals/information;
- forms/approvals/stamps/etc. as appropriate to your implementation;
- freeform manual notebook;
- meaningful simulated-time costs;
- successful filing;
- 5:00 PM failure;
- comedic catastrophic consequence;
- restart/new seed;
- `OUT TO LUNCH` fail-safe and diagnostic logging;
- enough generated variation that two runs are observably different.

The experience may still lack final polish, balance, content breadth, or presentation refinement.

### Checkpoint 2 report

Report:

- whether complete runs are currently possible;
- how many seeds you tested;
- whether all tested seeds were solvable;
- any `OUT TO LUNCH` activations and their causes;
- approximate run timing;
- major unfinished/polish areas;
- known bugs;
- what you intend to improve before Checkpoint 3.

Then stop.

---

# CHECKPOINT 3 — CONTENT, BALANCE, AND POLISH

Checkpoint 3 is reached when the full game has undergone a substantial polish pass.

Focus on:

- procedural variety;
- pacing;
- balance;
- comedy;
- NPC dialogue;
- legibility;
- navigation;
- visual cohesion;
- UI polish;
- sound/audio if appropriate;
- catastrophe variety;
- discoverability;
- interaction feel;
- time pressure;
- reduction of repetitive or generic content;
- bug fixing.

The game should increasingly feel authored despite being procedural.

### Checkpoint 3 report

Report:

- major improvements since Checkpoint 2;
- number of seeds tested;
- solvability results;
- run-duration observations;
- `OUT TO LUNCH` diagnostic summary;
- remaining known issues;
- remaining work required for a release candidate.

Then stop.

---

# CHECKPOINT 4 — RELEASE CANDIDATE

Checkpoint 4 is reached when you consider the game ready for player evaluation.

Before declaring this checkpoint:

1. perform a final regression pass;
2. test multiple fresh seeds;
3. verify success and 5:00 PM failure;
4. verify the notebook;
5. verify new-run generation;
6. inspect diagnostic logs;
7. remove obvious debug/placeholder artifacts from normal play;
8. ensure startup instructions are clear;
9. ensure the repository contains everything required to run the game, except dependencies that can be installed through clearly documented standard steps.

Create or update a concise `README.md` containing:

- what the game is;
- how to install/run it;
- controls;
- any required dependencies;
- known issues, if material.

### Checkpoint 4 report

Report:

- final implementation summary;
- engine/stack;
- how to run the game;
- number of final seeds tested;
- solvability results;
- observed run-duration range;
- number of genuine `OUT TO LUNCH` activations;
- known issues;
- any external assets/resources and licenses;
- anything the evaluator should know before blind playtesting.

Then stop.

Do not continue redesigning the game unless the user provides new instructions.

---

## 15. What Not to Do

Do not:

- ask the user to choose your engine;
- ask the user to choose between 2D and 3D;
- ask the user to select an art style;
- ask for user-created assets;
- ask for approval after every implementation decision;
- replace the notebook with an automatic quest tracker;
- knowingly generate unsolvable normal runs;
- use deliberate NPC lies as routine difficulty;
- treat `OUT TO LUNCH` as normal random content;
- omit the six-floor structure;
- remove the deadline;
- turn the project into a different genre;
- stop at a design document instead of implementing;
- declare completion without testing;
- hide material known failures from checkpoint reports.

---

## 16. Priority Order

When tradeoffs are necessary, prioritize in this order:

1. A functioning complete game loop.
2. Solvable procedural generation.
3. Player comprehension and usability.
4. The intended bureaucratic-comedy experience.
5. Replayability and variation.
6. Robustness.
7. Visual/audio polish.
8. Additional content.

A smaller finished game is preferable to a larger unfinished one.

---

## 17. Final Standard

The final result should make a player feel that they spent a ridiculous day trying to accomplish one tiny administrative task inside a bureaucracy that is internally logical, locally reasonable, globally maddening, and somehow responsible for preventing the end of the world.

Build that game.
