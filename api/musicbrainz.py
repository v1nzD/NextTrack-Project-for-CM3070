
# api/musicbrainz.py
import os
import time
import requests
import hashlib
from typing import Optional
from django.core.cache import cache

USER_AGENT = os.getenv("MB_USER_AGENT", "NextTrack/0.1 (your-email@example.com)")
BASE_URL = "https://musicbrainz.org/ws/2/recording/"
CACHE_TTL = 60 * 15  # 15 minutes
TIMEOUT = 6
RETRIES = 2

def _hash_key(prefix: str, raw: str) -> str:
    h = hashlib.md5(raw.encode("utf-8")).hexdigest()
    return f"{prefix}:{h}"

def _mb_get(params):
    last_err = None
    for _ in range(RETRIES + 1):
        try:
            r = requests.get(
                BASE_URL,
                params=params,
                headers={"User-Agent": USER_AGENT},
                timeout=TIMEOUT,
            )
            r.raise_for_status()
            return r.json()
        except requests.RequestException as e:
            last_err = e
            time.sleep(0.5)
    raise last_err

def _escape_lucene(value: str) -> str:
    if value is None:
        return ""
    return value.replace("\\", "\\\\").replace('"', '\\"')

def _artist_name(rec) -> str:
    return (rec.get("artist-credit", [{}])[0].get("name") or "").strip()

def _artist_mbid(rec) -> str:
    ac = rec.get("artist-credit", [{}])[0]
    artist = ac.get("artist") or {}
    return (artist.get("id") or "").strip()

def search_musicbrainz_track(track_name: str, artist_hint: Optional[str] = None):
    """
    Resolve a track to a single 'best' recording.
    - If artist_hint is provided, prefer candidates whose artist matches (case-insensitive).
    - Otherwise, choose the candidate with the most releases as a popularity proxy.
    """
    if not track_name:
        return None

    raw_title = track_name.strip()
    raw_artist = (artist_hint or "").strip()

    # cache key includes artist hint so different artists don't collide
    cache_key = _hash_key("mbz:first", f"{raw_title.lower()}|{raw_artist.lower()}")
    cached = cache.get(cache_key)
    if cached:
        return cached

    # Build Lucene query
    if raw_artist:
        q = f'recording:"{_escape_lucene(raw_title)}" AND artist:"{_escape_lucene(raw_artist)}"'
    else:
        q = f'recording:"{_escape_lucene(raw_title)}"'

    try:
        data = _mb_get({"query": q, "fmt": "json", "limit": 10})
    except requests.RequestException as e:
        print(f"[MB] error: {e}")
        return None

    recs = data.get("recordings") or []
    if not recs:
        return None

    # If artist_hint is provided, try exact artist match first
    if raw_artist:
        cand = [r for r in recs if _artist_name(r).lower() == raw_artist.lower()]
        if cand:
            recs = cand

    # Heuristic: pick the recording with the most releases
    def release_count(r):
        return len(r.get("releases") or [])

    best = max(recs, key=release_count)

    result = {
        "title": best.get("title"),
        "artist": _artist_name(best) or "Unknown Artist",
        "artist_mbid": _artist_mbid(best) or "",
        "track_id": best.get("id"),
        "release-group": best.get("release-group") or {},
    }
    cache.set(cache_key, result, CACHE_TTL)
    return result


def search_musicbrainz_recordings(query: str, limit: int = 25, offset: int = 0):
    """Generic multi-recording search by a Lucene query string."""
    if not query:
        return []
    cache_key = _hash_key("mbz:recs", f"{limit}:{offset}:{query}")
    cached = cache.get(cache_key)
    if cached:
        return cached
    try:
        data = _mb_get({
            "query": query,
            "fmt": "json",
            "limit": limit,
            "offset": offset,
            "inc": "tags+release-groups",   # request extra info
        })
    except requests.RequestException as e:
        print(f"[MB] error: {e}")
        return []
    recs = data.get("recordings") or []
    cache.set(cache_key, recs, CACHE_TTL)
    return recs



def search_recordings_by_artist(artist_name: str, exclude_title: Optional[str] = None, limit: int = 25):
    """
    Query recordings by artist, optionally excluding a specific title.
    Uses MusicBrainz Lucene query: artist:"..." AND NOT recording:"..."
    """
    if not artist_name:
        return []
    a = _escape_lucene(artist_name)
    q = f'artist:"{a}"'
    if exclude_title:
        t = _escape_lucene(exclude_title)
        q += f' AND NOT recording:"{t}"'
    return search_musicbrainz_recordings(q, limit=limit)


def search_recordings_by_artist_mbid(artist_mbid: str, exclude_title: Optional[str] = None, limit: int = 25):
    """
    Query recordings by artist MBID, optionally excluding a specific title.
    Lucene field for MBID is 'arid' (artist id).
    """
    if not artist_mbid:
        return []
    q = f'arid:{_escape_lucene(artist_mbid)}'
    if exclude_title:
        q += f' AND NOT recording:"{_escape_lucene(exclude_title)}"'
    return search_musicbrainz_recordings(q, limit=limit)


def fetch_cover_art(release_group_id):
    if not release_group_id:
        return None
    url = f"https://coverartarchive.org/release-group/{release_group_id}"
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        if "images" in data and data["images"]:
            return data["images"][0].get("image")
    except Exception:
        return None

