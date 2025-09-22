from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, throttling
import random
from .musicbrainz import (
    search_musicbrainz_track,
    search_recordings_by_artist,
    search_recordings_by_artist_mbid,
    search_musicbrainz_recordings,
    fetch_cover_art
)
from .serializers import (
    RecommendRequestSerializer,
    RecommendResponseSerializer,
    RecommendTopResponseSerializer
)

# This view handles the recommendation logic based on recent tracks and user preferences.
class RecommendView(APIView):
    # Optional throttling hook (enable later in settings if you want)
    throttle_classes = [throttling.AnonRateThrottle]

    def post(self, request):
        req = RecommendRequestSerializer(data=request.data)
        req.is_valid(raise_exception=True)

        recent_tracks = req.validated_data["recent_tracks"]
        preferences = req.validated_data.get("preferences", {}) or {}

        track_name = recent_tracks[0]
        artist_hint = (preferences.get("artist") or "").strip()

        # pass artist_hint to improve disambiguation (e.g., "Bad Guy" → Billie Eilish)
        metadata = search_musicbrainz_track(track_name, artist_hint=artist_hint)

        if not metadata:
            return Response(
                {"error": "Track not found in MusicBrainz"},
                status=status.HTTP_404_NOT_FOUND
            )

        payload = {
            "recommended_track": {
                "id": metadata["track_id"],
                "artist": metadata["artist"],
                "title": metadata["title"],
                "genre": preferences.get("genre", "unknown"),
                "mood": preferences.get("mood", "unknown"),
            }
        }
        # (Optional) validate your response shape too
        res = RecommendResponseSerializer(data=payload)
        res.is_valid(raise_exception=True)

        return Response(res.data, status=status.HTTP_200_OK)


# mood→genre map to nudge scoring
MOOD_GENRE_MAP = {
    "happy": ["pop", "dance", "electronic", "funk"],
    "sad": ["acoustic", "indie", "piano", "alternative"],
    "angry": ["rock", "metal", "punk", "trap"],
    "chill": ["lo-fi", "ambient", "jazz", "r&b"],
    "romantic": ["r&b", "soul", "ballad", "pop"],
    "energetic": ["edm", "hip-hop", "pop", "trap"],
}


class RecommendTopView(APIView):
    def post(self, request):
        # Validate request
        req = RecommendRequestSerializer(data=request.data)
        req.is_valid(raise_exception=True)

        recent_tracks = req.validated_data["recent_tracks"]
        preferences = req.validated_data.get("preferences", {}) or {}

        mood = (preferences.get("mood") or "").lower()
        genre_hint = (preferences.get("genre") or "").lower()
        artist_hint = (preferences.get("artist") or "").strip()
        randomize = bool(preferences.get("randomize") or False)
        seed = preferences.get("seed")
        genre_prefs = MOOD_GENRE_MAP.get(mood, [])

        # 1) Resolve seed track
        input_title = recent_tracks[0]
        seed_rec = search_musicbrainz_track(input_title, artist_hint=artist_hint)
        if not seed_rec:
            return Response(
                {"error": "Track not found in MusicBrainz"},
                status=status.HTTP_404_NOT_FOUND,
            )

        seed_title = (seed_rec.get("title") or "").lower()
        seed_artist = seed_rec.get("artist") or ""
        seed_artist_mbid = seed_rec.get("artist_mbid") or ""

        # 2) Fetch candidates
        if seed_artist_mbid:
            results = search_recordings_by_artist_mbid(
                seed_artist_mbid, exclude_title=seed_rec.get("title"), limit=50
            )
        else:
            results = search_recordings_by_artist(
                seed_artist, exclude_title=seed_rec.get("title"), limit=50
            )

        # Optional: randomized pagination fallback
        if len(results) < 10 and randomize:
            offset = random.randint(0, 200)
            results += search_musicbrainz_recordings(
                input_title, limit=50, offset=offset
            )

        # 3) Scoring
        def score(rec):
            s = 0
            title = (rec.get("title") or "").lower()
            artist_name = (
                rec.get("artist-credit", [{}])[0].get("name") or ""
            ).lower()

            # Same artist
            if artist_name and seed_artist.lower() == artist_name:
                s += 5  # stronger weight

            # Same album (release group)
            if rec.get("release-group") and seed_rec.get("release-group"):
                if (
                    rec["release-group"].get("id")
                    == seed_rec["release-group"].get("id")
                ):
                    s += 3

            # Tags vs user preference
            tags = [t.get("name", "").lower() for t in rec.get("tags", [])]
            if genre_hint and genre_hint in tags:
                s += 2
            for g in genre_prefs:
                if g in tags:
                    s += 2
                    break

            # Light heuristic: mood/genre keyword in title
            if genre_hint and genre_hint in title:
                s += 1

            # Penalize exact duplicate
            if title == seed_title:
                s -= 10

            return s

        ranked = sorted(results, key=score, reverse=True)

        # 4) Build candidate pool with diversity
        pool, seen_titles = [], set()
        artist_count, album_count = {}, {}

        for rec in ranked:
            title = (rec.get("title") or "").strip()
            if not title:
                continue
            tkey = title.lower()
            if tkey == seed_title or tkey in seen_titles:
                continue

            artist_credit = rec.get("artist-credit", [{}])[0]
            artist_name = artist_credit.get("name") or "Unknown Artist"
            artist_mbid = artist_credit.get("artist", {}).get("id") or artist_name
            album_id = (
                rec.get("release-group", {}).get("id")
                if rec.get("release-group")
                else None
            )

            # Diversity constraint: max 2 per artist, max 2 per album
            if artist_count.get(artist_mbid, 0) >= 2:
                continue
            if album_id and album_count.get(album_id, 0) >= 2:
                continue

            cover_art = fetch_cover_art(album_id)

            pool.append(
                {
                    "id": rec.get("id"),
                    "title": title,
                    "artist": artist_name,
                    "mood": mood or "unknown",
                    "genre_hint": genre_hint or "unknown",
                    "cover_art": cover_art,
                }
            )
            seen_titles.add(tkey)

            # increment counts
            artist_count[artist_mbid] = artist_count.get(artist_mbid, 0) + 1
            if album_id:
                album_count[album_id] = album_count.get(album_id, 0) + 1

            if len(pool) >= 30:  # cap pool size
                break

        # Relax constraint if too few
        if len(pool) < 5:
            for rec in ranked:
                if len(pool) >= 5:
                    break
                title = (rec.get("title") or "").strip()
                if not title:
                    continue
                tkey = title.lower()
                if tkey == seed_title or tkey in seen_titles:
                    continue

                artist_credit = rec.get("artist-credit", [{}])[0]
                artist_name = artist_credit.get("name") or "Unknown Artist"
                artist_mbid = artist_credit.get("artist", {}).get("id") or artist_name
                album_id = (
                    rec.get("release-group", {}).get("id")
                    if rec.get("release-group")
                    else None
                )
                cover_art = fetch_cover_art(album_id)

                pool.append(
                    {
                        "id": rec.get("id"),
                        "title": title,
                        "artist": artist_name,
                        "mood": mood or "unknown",
                        "genre_hint": genre_hint or "unknown",
                        "cover_art": cover_art,
                    }
                )
                seen_titles.add(tkey)

        # If no pool → 404
        if not pool:
            return Response(
                {"error": "No suitable recommendations found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # 5) Randomize selection
        if randomize:
            rnd = random.Random(str(seed) if seed is not None else None)
            candidate_pool = pool[:10] if len(pool) > 10 else pool
            rnd.shuffle(candidate_pool)
            top = candidate_pool[:5]
        else:
            top = pool[:5] if len(pool) >= 5 else pool

        # Validate response
        resp = {"recommended_tracks": top}
        out = RecommendTopResponseSerializer(data=resp)
        out.is_valid(raise_exception=True)

        return Response(out.data, status=status.HTTP_200_OK)
