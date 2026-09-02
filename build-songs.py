#!/usr/bin/env python3
"""Regenerate songs.js from the public iTunes catalogue.

Run this when Laufey releases something new:  python3 build-songs.py
"""
import json, re, time, urllib.parse, urllib.request

ARTIST_ID = 1504424880  # Laufey
URLS = [
    f"https://itunes.apple.com/lookup?id={ARTIST_ID}&entity=song&limit=400&country=US",
    # The Lofi Collection sits outside the main catalogue listing, so ask for it directly.
    "https://itunes.apple.com/search?term=laufey+lofi&entity=song&limit=50&country=US",
]

LOFI = re.compile(r'\(lofi version\)', re.I)

# Soundalikes for Laufi mode: same hushed jazz/bedroom-pop lane, not Laufey.
# Titles that collide with a Laufey song (e.g. Samara Joy's "Misty") are left
# out so the dropdown never shows two identical entries.
DECOY_TRACKS = [
    ("Lauren Rose", "Chills"),
    ("Lauren Rose", "Stuck On My Mind"),
    ("Lauren Rose", "Mystery of Life"),
    ("Lauren Rose", "I Should Care"),
    ("Samara Joy", "Guess Who I Saw Today"),
    ("Samara Joy", "Can't Get Out of This Mood"),
    ("Samara Joy", "Stardust"),
    ("Samara Joy", "I Miss You So"),
    ("Melody Gardot", "Baby I'm a Fool"),
    ("Melody Gardot", "If the Stars Were Mine"),
    ("Melody Gardot", "Worrisome Heart"),
    ("Madeleine Peyroux", "Don't Wait Too Long"),
    ("Madeleine Peyroux", "Dance Me To the End of Love"),
    ("Madeleine Peyroux", "The Summer Wind"),
    ("Cathy Jain", "green screen"),
    ("Cathy Jain", "cool kid"),
    ("Sarah Kinsley", "The King"),
    ("Sarah Kinsley", "Karma"),
    ("Olivia Dean", "The Hardest Part"),
    ("Rachael Yamagata", "Be Be Your Love"),
    ("beabadoobee", "Glue Song"),
    ("beabadoobee", "The Perfect Pair"),
]

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
titles_taken = {norm(s['title']) for s in songs}


def fetch_decoy(artist, title):
    """Find one soundalike track, matching on both artist and title."""
    q = urllib.parse.quote(f'{artist} {title}')
    url = f'https://itunes.apple.com/search?term={q}&entity=song&limit=15&country=US'
    for attempt in range(5):
        try:
            results = json.load(urllib.request.urlopen(url, timeout=20))['results']
            break
        except Exception:
            time.sleep(4 * (attempt + 1))     # iTunes rate-limits bursts of searches
    else:
        print(f'  ! lookup failed: {artist} — {title}')
        return None
    for r in results:
        if not r.get('previewUrl'): continue
        if r['artistName'].lower() != artist.lower(): continue
        if norm(r['trackName']) != norm(title): continue
        return {
            'title': tidy(r['trackName']),
            'artist': r['artistName'],
            'album': tidy(r['collectionName']),
            'year': r.get('releaseDate', '????')[:4],
            'art': r['artworkUrl100'].replace('100x100', '400x400'),
            'preview': r['previewUrl'],
        }
    print(f'  ! no match: {artist} — {title}')
    return None


decoys = []
for artist, title in DECOY_TRACKS:
    d = fetch_decoy(artist, title)
    if not d: continue
    if norm(d['title']) in titles_taken:          # would duplicate a Laufey entry
        print(f'  ! title clashes with a Laufey song, skipping: {d["title"]}')
        continue
    decoys.append(d)
    titles_taken.add(norm(d['title']))
    time.sleep(2.0)
decoys.sort(key=lambda d: d['title'].lower())

with open('songs.js', 'w') as f:
    f.write('const SONGS = ' + json.dumps(songs, ensure_ascii=False, separators=(',', ':')) + ';\n')
    f.write('const DECOYS = ' + json.dumps(decoys, ensure_ascii=False, separators=(',', ':')) + ';\n')
print(f'wrote songs.js — {len(songs)} songs, {len(decoys)} decoys')
