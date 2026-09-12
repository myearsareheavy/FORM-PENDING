# Form Pending

A short, replayable bureaucracy simulator.

You enter a six-story municipal building at **8:00 AM** with one ordinary document. It must be properly filed before the office closes at **5:00 PM**. Filing it will not be ordinary.

There is no quest log. Clerks tell you fragments. If something matters, write it down.

## Install

Python 3.10 or later, and pygame.

```
py -3 -m pip install -r requirements.txt
```

On some systems that is `python3` or `python` instead of `py -3`.

## Run

From this folder:

```
py -3 main.py
```

or:

```
py -3 -m form_pending
```

To reproduce a shift, pass a seed:

```
py -3 main.py 42
```

You can also type a seed on the title page. Leave it blank for a random day.

The current seed is shown in the top-right during a shift.

## Controls

| Key | Action |
| --- | --- |
| WASD / arrows | Walk |
| E / Space | Talk, use the elevator, read a directory or wall notice |
| N | Notebook (ESC closes it) |
| R | Read the visitor transmittal you walked in with |
| 1–6 | Pick a floor while standing in the elevator |
| Enter | Begin a shift / begin another after an ending |
| ESC | Close a panel, or return to the title from an ending |
| M | Mute |

The notebook is blank on purpose. The game will not copy conversations into it.

## What you are doing

You have until 5:00. The building is one structure with six color-coded floors and an elevator that always opens in the same place. People at desks know their own job, not the whole chain.

Failure and success both end the day. Enter starts a new one.

## Tests (optional)

```
py -3 tests/test_generate.py
py -3 tests/test_notebook.py
py -3 tests/test_loop.py
py -3 tests/test_smoke.py
py -3 tests/test_release.py
```

## Known issues

- How long a first run takes depends on how much you wander. Standing still, the clock covers a full day in about an hour of real time. Moving, talking, and riding the elevator spend additional minutes.
- There is no objective tracker. That is the game.
- Sound is generated in-engine. If your mixer is unavailable, the game still runs silent.

## License / assets

Original code and procedurally drawn graphics. No third-party art or audio packs. pygame is used under its LGPL license.
