# Laufeyless

A Heardle-style guessing game for Laufey's catalogue. You get one second of a song — name it, or skip and hear more.

**Play: https://aidiotic.github.io/laufeyless/**

## How it works

Six tries. A wrong guess or a skip unlocks the next clip length:

`1s → 2s → 4s → 7s → 11s → 16s`

- **Daily** — the same song for everyone, changing at midnight. A seeded permutation means no repeats until all 76 songs have been used.
- **Endless** — random, forever, and it doesn't touch your daily stats.

Streaks, win rate and a guess distribution are kept in `localStorage`. Nothing leaves your browser.

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
