# Laufeyless

A Heardle-style guessing game for Laufey's catalogue. You get one second of a song — name it, or skip and hear more.

**Play: https://aidiotic.github.io/laufeyless/**

## How it works

Six tries. A wrong guess or a skip unlocks the next clip length:

`1s → 2s → 4s → 7s → 11s → 16s`

- **Daily** — the same song for everyone, changing at midnight. A seeded permutation means no repeats until all 77 songs have been used.
- **Endless** — random, forever, and it doesn't touch your daily stats.
- **Insane `^`** — a much tighter ladder over seven tries: `0.1 → 0.5 → 0.6 → 1 → 1.2 → 1.5 → 2s`. Pays roughly triple, and wins are tagged `^`.
- **Laufi `~`** — lofi only, with soundalike decoys. Normal ladder, top pay rate, wins tagged `~`.

Insane and Laufi give you **no hints**.

### Laufi decoys

Laufi plays only lofi-flavoured tracks, and the pool is her four Lofi Versions plus 21 tracks from artists in the same hushed jazz/bedroom-pop lane — Lauren Rose, Samara Joy, Melody Gardot, Madeleine Peyroux, Cathy Jain, Sarah Kinsley, Olivia Dean, Rachael Yamagata, beabadoobee.

The pick is weighted so roughly **half the rounds are actually Laufey**; otherwise 21 decoys would drown out four real songs. So the question each round is both "which song is this?" and "is this even her?". The dropdown lists the artist next to each title, and the reveal says outright whether you just heard a Lofi Version or a decoy.

Decoy titles that would collide with a Laufey song are dropped at build time — that's why Samara Joy's "Misty" isn't in there.

### Lofi versions

Four songs have an official *Lofi Version* (Falling Behind, From The Start, I Wish You Love, Valentine). Rather than adding them as separate answers — which would put two near-identical entries in the dropdown and mark a correct-sounding guess wrong — they're wired as **alternate audio for the same answer**. In insane mode those four play their lofi cut instead: same title to guess, different arrangement to recognise. The reveal tells you which one you heard.

### Volume

A slider sits in the transport row and drives both the clip player and the full-preview player on the reveal screen. The speaker icon toggles mute, dragging to zero mutes, and the level is remembered in `localStorage`. (iOS Safari doesn't allow scripted volume changes on media elements, so there you'll need the hardware buttons.)

### Hint

**Reveal first letters** gives you the opening two letters of the title — deliberately never a whole word, so you still have to place the song yourself:

| Title | Hint |
|-------|------|
| Fragile | `Fr…` |
| A Cautionary Tale | `A Ca…` |
| Hi | `H…` |

A leading "A" or "The" is shown but skipped over, otherwise the hint gets spent on the article. Words shorter than three letters give up one letter rather than all of them. Checked against the whole catalogue: no title's hint spells out the title.

It costs 25 points and tags the win with `&*`, on the guess row, the leaderboard and the shared result — so a hinted solve is always distinguishable from a clean one.

### Scoring

Points by the clip length you solved at, minus 25 if you took the hint.

Normal (daily / endless):

| 1s | 2s | 4s | 7s | 11s | 16s | missed |
|----|----|----|----|-----|-----|--------|
| 100 | 80 | 60 | 45 | 30 | 20 | 0 |

Insane `^`:

| 0.1s | 0.5s | 0.6s | 1s | 1.2s | 1.5s | 2s | missed |
|------|------|------|----|------|------|----|--------|
| 300 | 240 | 190 | 150 | 115 | 85 | 60 | 0 |

Laufi `~` (top rate, decoys, no hints):

| 1s | 2s | 4s | 7s | 11s | 16s | missed |
|----|----|----|----|-----|-----|--------|
| 400 | 320 | 250 | 190 | 145 | 105 | 0 |

Since insane and laufi pay several times normal, they dominate the top of the leaderboard — the `^` tag is there so you can tell at a glance which runs were earned the hard way.

### Leaderboard

The ♔ button ranks your best 50 runs by score. It's **local to your device** — this is a static site with no backend, so there's no cross-player board. Making it global would mean adding a small serverless store and some abuse handling.

Both the leaderboard and the result screen have a **Copy for Claude** button that dumps a plain-text report — stats, latest result, top runs — ready to paste into a chat.

Streaks, win rate, guess distribution and the leaderboard all live in `localStorage`. Nothing leaves your browser.

## The music

76 songs, covering the studio albums, the Christmas EPs, *Typical of Me*, and the soundtrack work. Instrumentals, sped-up edits, remixes and live re-recordings are filtered out, and the album / single / deluxe cuts of the same title are deduped down to one.

Audio is Apple's public 30-second preview clips. Those are cut to start at the song's hook rather than the first note, so this plays a little differently from the original Heardle — you get the recognisable part up front.

## Updating the catalogue

`songs.js` is generated, not hand-maintained. After a new release:

```bash
python3 build-songs.py
```

That re-queries the iTunes catalogue, re-applies the filtering and dedupe rules, and rewrites `songs.js`.

## Running locally

Three static files, no dependencies, no build step:

```bash
npx serve
```

## Notes

Unofficial fan project. All music © Laufey & AWAL — this only links to the same preview clips Apple serves publicly.
