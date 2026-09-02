#!/usr/bin/env python3
"""Regenerate songs.js from the public iTunes catalogue.

Run this when Laufey releases something new:  python3 build-songs.py
"""
import json, re, urllib.request

ARTIST_ID = 1504424880  # Laufey
URLS = [
    f"https://itunes.apple.com/lookup?id={ARTIST_ID}&entity=song&limit=400&country=US",
    # The Lofi Collection sits outside the main catalogue listing, so ask for it directly.
    "https://itunes.apple.com/search?term=laufey+lofi&entity=song&limit=50&country=US",
]

LOFI = re.compile(r'\(lofi version\)', re.I)

# Versions that would either duplicate a song or make it unfairly hard to name.
BAD_COLLECTION = re.compile(r'instrumental|sped up|remix', re.I)
BAD_TRACK = re.compile(r'instrumental|sped up|remix|\blive\b|interlude|intro\b|outro\b|reprise', re.I)


def norm(name):
    """Collapse a title to a comparison key so album/single/deluxe cuts dedupe."""
    name = re.sub(r'\s*[\(\[][^)\]]*[\)\]]', '', name)
    name = re.sub(r'\s*-\s*(single|live|sped up|instrumental).*$', '', name, flags=re.I)
    name = re.sub(r'\s*feat\..*$', '', name, flags=re.I)
    return re.sub(r'[^a-z0-9]', '', name.lower())


def score(track):
    """Lower is better. Prefers the original studio cut over symphony/live/reissues."""
    coll, s = track['collectionName'], 0
    if 'Symphony' in coll or 'Hollywood Bowl' in coll: s += 40
    if 'Reykjavík Sessions' in coll: s += 30
    if BAD_COLLECTION.search(coll): s += 100
    if '- Single' in coll or '- EP' in coll: s += 5
    if any(w in coll for w in ('Deluxe', 'Edition', 'Hour', 'Goddess')): s += 2
    return s + track.get('trackNumber', 50) * 0.001


def tidy(text):
    text = re.sub(r'\s*\((Bonus Track|Take \d+|feat\.[^)]*)\)', '', text, flags=re.I)
    return re.sub(r'\s*-\s*(Single|EP|Live).*$', '', text, flags=re.I).strip()


results = {}
for url in URLS:
    with urllib.request.urlopen(url) as r:
        for t in json.load(r)['results']:
            if t.get('wrapperType') == 'track' or t.get('kind') == 'song':
                results[t.get('trackId')] = t
results = list(results.values())

best, lofi = {}, {}
for t in results:
    if not t.get('previewUrl'): continue
    if t['artistName'] != 'Laufey' and 'Laufey' not in t['artistName']: continue
    key = norm(t['trackName'])
    if not key: continue
    # Lofi cuts are alternate takes of songs already in the pool, not new answers.
    if LOFI.search(t['trackName']):
        if key not in lofi: lofi[key] = t['previewUrl']
        continue
    if BAD_TRACK.search(t['trackName']): continue
    if BAD_COLLECTION.search(t['collectionName']): continue
    if key not in best or score(t) < score(best[key]):
        best[key] = t

def entry(key, t):
    s = {
        'title': tidy(t['trackName']),
        'artist': t['artistName'],
        'album': tidy(t['collectionName']),
        'year': t['releaseDate'][:4],
        'art': t['artworkUrl100'].replace('100x100', '400x400'),
        'preview': t['previewUrl'],
    }
    if key in lofi:            # same answer, different arrangement — used by insane mode
        s['lofi'] = lofi[key]
    return s

songs = sorted((entry(k, t) for k, t in best.items()), key=lambda s: s['title'].lower())

with open('songs.js', 'w') as f:
    f.write('const SONGS = ' + json.dumps(songs, ensure_ascii=False, separators=(',', ':')) + ';\n')
print(f'wrote songs.js — {len(songs)} songs')
