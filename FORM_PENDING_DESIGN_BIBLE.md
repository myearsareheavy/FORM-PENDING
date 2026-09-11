# Form Pending --- Project Design Bible

> **Status:** Experimental build specification\
> **Purpose:** Shared creative brief for autonomous coding-agent
> comparison\
> **Working title:** *Form Pending*

## 1. Concept

*Form Pending* is a short, replayable bureaucracy simulator built around
an intentionally absurd procedural administrative maze.

The player enters a six-story government/administrative building at
**8:00 AM** carrying a document that absolutely must be properly filed
before the office closes at **5:00 PM**.

Filing the document should sound trivial.

It is not.

The player discovers that filing it requires a chain of forms,
signatures, stamps, approvals, corrections, copies, conversations,
offices, departments, and prerequisites. The precise bureaucratic chain
changes between games.

The player's actual enemy is **bureaucracy**.

There is no conventional villain. NPCs should generally be doing their
jobs as they understand them. The system itself creates the absurdity.

A successful first-time playthrough should take approximately **45--60
real-world minutes**. Repeat runs should remain interesting because the
solution cannot simply be memorized.

------------------------------------------------------------------------

## 2. Core Player Fantasy

The player should repeatedly experience:

> "This should be easy."

followed by:

> "You've got to be fucking kidding me."

That cycle is the heart of the game.

The humor should emerge primarily from the collision between **mundane
administrative procedure** and **wildly disproportionate consequences**.

For example, the player may simply need Form P91-2X stamped by Records
Processing.

Failure to accomplish this before 5:00 PM might result in:

-   nuclear annihilation;
-   the moon falling from orbit;
-   revocation of Tuesday;
-   catastrophic temporal collapse;
-   the player's house being rezoned as a municipal parking structure;
-   the extinction of an inexplicably specific species; or
-   another similarly absurd catastrophe.

The bureaucracy itself should treat these stakes as completely ordinary.

------------------------------------------------------------------------

## 3. Tone

The game is **dry, absurd, frustrating, funny, mundane, slightly
surreal, and increasingly frantic**.

It should **not** feel cruel toward ordinary workers.

The joke is institutional absurdity---not "government employees are
stupid."

NPCs generally possess limited information because they occupy one tiny
piece of an enormous system.

Someone may truthfully tell the player:

> "You'll need Janet for that."

They may have absolutely no idea where Janet is.

Janet may work three floors away. Someone else knows where Janet sits
but doesn't know whether Janet is currently there. Janet knows exactly
what the player needs---but first needs Form 17-C.

This is bureaucracy functioning exactly as designed.

------------------------------------------------------------------------

## 4. Visual Direction

**The visual style is deliberately not prescribed.**

Do not assume pixel art.

The game should have a distinctive, coherent visual identity appropriate
to:

-   bureaucratic absurdity;
-   readable navigation;
-   a somewhat charming presentation;
-   escalating comedic frustration; and
-   a relatively small game scope.

The implementing system is free to determine an appropriate aesthetic
and asset-production strategy.

Possible influences can include retro games, stylized office
illustration, low-poly environments, hand-drawn animation, limited-color
graphic design, pixel art, or another coherent direction.

These are inspirations, **not requirements**.

The resulting game should look intentionally designed rather than like a
generic developer prototype.

------------------------------------------------------------------------

## 5. World Structure

The game takes place primarily inside **one six-story administrative
building**.

Each floor should be immediately distinguishable. Color coding is
encouraged but not required.

Floors contain some combination of:

-   cubicles;
-   offices;
-   counters;
-   waiting areas;
-   elevators and/or stairs;
-   corridors;
-   printers/copiers;
-   administrative departments;
-   NPC workstations; and
-   environmental signage.

The building should be understandable enough that players can gradually
construct a mental map.

However, the exact layout should change between runs.

Procedural generation must never intentionally produce an impossible
game state.

------------------------------------------------------------------------

## 6. NPC Population

The building should feel populated by a large number of visually
distinguishable but deliberately ordinary employees.

Think roughly **dozens to around 100 potential NPC identities**, rather
than 100 bespoke characters requiring unique narrative arcs.

NPCs should have procedurally generated or selected:

-   names;
-   appearances;
-   departments;
-   locations;
-   roles; and
-   limited pieces of bureaucratic knowledge.

NPCs should be distinguishable enough that remembering the correct
person matters.

"Janet" should be a person the player can actually find again.

But Janet should not look like the Chosen One.

She's Janet.

------------------------------------------------------------------------

## 7. Information Is Gameplay

There is **no automatic quest log** that converts conversations into
objectives.

The player receives information by:

-   speaking with NPCs;
-   reading signs;
-   examining forms;
-   exploring;
-   following referrals; and
-   remembering things.

The player has access to a simple **manual notebook**.

The game does **not** decide what information is important. The player
does.

If an NPC says:

> "Janet handles those. Fourth floor, I think. She used to sit near
> Procurement."

the player may write that down---or not.

The notebook should permit freeform player-entered notes.

Taking good notes should confer a genuine advantage.

------------------------------------------------------------------------

## 8. NPC Information Rules

NPCs may be:

-   incomplete;
-   overly literal;
-   irrelevant;
-   repetitive;
-   irritatingly specific;
-   irritatingly vague; or
-   unaware of information outside their responsibility.

However:

**NPCs should not deliberately lie to the player merely to manufacture
difficulty.**

Difficulty should emerge from fragmented information and bureaucratic
dependencies.

The player should eventually be able to reason through the system.

------------------------------------------------------------------------

## 9. Procedural Bureaucracy

This is the technical and design heart of the game.

Every new game should generate a **solvable dependency structure**
between the player's starting document and successful filing.

Conceptually:

`Goal → requirement → prerequisite → person → form → approval → additional prerequisite → ...`

For example:

``` text
P91-2X
└── requires blue validation stamp
    └── validation requires Form 17-C
        └── 17-C comes from Records
            └── Records requires supervisor signature
                └── supervisor needs identity verification
                    └── verification requires Copy B
                        └── copier on Floor 2 is broken
                            └── working copier is on Floor 5
```

The player then works back through the chain until P91-2X can finally be
filed.

This example is illustrative only. The system should generate its own
coherent chains.

Some branches can be unnecessary or distracting simply because the
player investigates the wrong department.

The **correct chain must always be completable**.

------------------------------------------------------------------------

## 10. The Clock

Each run begins at **8:00 AM**.

The building closes at **5:00 PM**.

Approximately nine simulated hours correspond to a target maximum of
roughly **one real-world hour**.

Actions may consume simulated time, including:

-   walking;
-   elevator travel;
-   waiting;
-   conversations;
-   administrative processing;
-   copying documents; and
-   obtaining approvals.

The clock should create mounting pressure without making careful
exploration impossible from the beginning.

The final portion of the day should feel meaningfully more stressful
than 8:15 AM.

------------------------------------------------------------------------

## 11. Failure

At exactly **5:00 PM**, an unfinished filing becomes a failure.

Failure should trigger a **short, dramatic, ridiculous game-over
sequence appropriate to that run's stated stakes**.

For example:

``` text
5:00 PM.

The clerk calmly flips the sign to CLOSED.

Beat.

White flash.

Mushroom cloud.

FORM P91-2X WAS NOT PROCESSED
```

The contrast is the joke.

Afterward, the player can begin another procedurally generated run.

------------------------------------------------------------------------

## 12. "Out to Lunch" --- Diegetic Fail-Safe

The procedural system must detect impossible or corrupted dependency
states.

The player should **never be expected to debug the game**.

If an NPC or dependency becomes unavailable because of an internal
generation failure, the game may present that NPC as:

> **OUT TO LUNCH**

This is a diegetic fail-safe rather than an ordinary gameplay obstacle.

Internally, however, the event must be logged with sufficient diagnostic
information to identify why generation failed.

This provides both:

1.  an immersion-preserving error state; and
2.  a measurable robustness metric during development.

A correctly functioning procedural generator should make genuine **Out
to Lunch** failures rare.

------------------------------------------------------------------------

## 13. What Must Remain Variable

Replayability should come from meaningful recombination of:

-   building layout;
-   NPC identities;
-   NPC locations;
-   departments;
-   document requirements;
-   dependency chains;
-   referrals;
-   administrative obstacles;
-   end-of-day catastrophe; and
-   incidental dialogue.

The player should learn **how to navigate bureaucracy**, not memorize a
solution.

------------------------------------------------------------------------

## 14. Scope

This is deliberately a **small game**.

The objective is not to build an enormous simulation.

Prefer:

> **one excellent systemic joke with surprising depth**

over:

> **twenty shallow mechanics**

No combat is required.

No elaborate character progression is required.

No enormous narrative campaign is required.

The desired experience is a complete, polished, replayable game that
demonstrates procedural design and strong creative judgment.

------------------------------------------------------------------------

## 15. Creative Freedom

Anything not explicitly identified as a non-negotiable requirement is
available for interpretation.

In particular, the implementing system should independently determine:

-   visual style;
-   asset creation strategy;
-   engine and technical stack;
-   camera/perspective;
-   control scheme;
-   UI design;
-   audio direction;
-   procedural-generation architecture;
-   exact building layouts;
-   exact number of NPCs;
-   dialogue presentation;
-   navigation aids;
-   pacing mechanics;
-   comedy writing; and
-   title, if a better one emerges.

**Make decisions rather than repeatedly asking for preferences when this
design bible provides enough information to exercise reasonable creative
judgment.**

Document consequential assumptions.

------------------------------------------------------------------------

## 16. Non-Negotiables

The following requirements are fixed for the comparison:

-   Six-story administrative building.
-   8:00 AM--5:00 PM in-game day.
-   Approximately one-hour maximum real-world run.
-   One seemingly trivial document-filing objective.
-   Procedurally generated, **solvable** bureaucratic dependency maze.
-   Meaningfully different runs.
-   Information obtained through exploration and NPC interaction.
-   Manual free-text notebook; no automatic quest log.
-   NPCs can be unhelpful but should not simply lie.
-   Absurdly disproportionate stakes.
-   Dramatic comedic failure at 5:00 PM.
-   **Out to Lunch** as a diegetic procedural-error mechanism with
    underlying diagnostic logging.
-   The finished product should feel like a **game**, not a tech demo.
-   Creative and technical decisions not specified here belong to the
    implementing system.

------------------------------------------------------------------------

## 17. Implementation Principle

This document intentionally specifies the **experience and
constraints**, not the implementation.

Do not infer an unstated requirement to use:

-   a particular game engine;
-   2D or 3D;
-   pixel art;
-   a premade asset pack;
-   a particular programming language;
-   a specific procedural-generation algorithm; or
-   a particular project architecture.

Choose an approach that best serves the game and can reasonably produce
a polished, playable result within the project's deliberately limited
scope.
