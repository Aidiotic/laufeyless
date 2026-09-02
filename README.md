# Laufeyless

A Heardle-style guessing game for Laufey's catalogue. You get one second of a song — name it, or skip and hear more.

**Play: https://aidiotic.github.io/laufeyless/**

## How it works

Six tries. A wrong guess or a skip unlocks the next clip length:

`1s → 2s → 4s → 7s → 11s → 16s`

- **Daily** — the same song for everyone, changing at midnight. A seeded permutation means no repeats until all 76 songs have been used.
- **Endless** — random, forever, and it doesn't touch your daily stats.

### Volume

A slider sits in the transport row and drives both the clip player and the full-preview player on the reveal screen. The speaker icon toggles mute, dragging to zero mutes, and the level is remembered in `localStorage`. (iOS Safari doesn't allow scripted volume changes on media elements, so there you'll need the hardware buttons.)

### Hint

**Reveal first word** gives you the first word of the *title* (a leading "A" or "The" comes with the next word attached, since "A" on its own helps nobody). It costs 25 points and tags the win with `&*`, on the guess row, the leaderboard and the shared result — so a hinted solve is always distinguishable from a clean one.

### Scoring

Points by the clip length you solved at, minus 25 if you took the hint:

| 1s | 2s | 4s | 7s | 11s | 16s | missed |
|----|----|----|----|-----|-----|--------|
| 100 | 80 | 60 | 45 | 30 | 20 | 0 |

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
