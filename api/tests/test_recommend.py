import json
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from unittest.mock import patch
from api.musicbrainz import search_musicbrainz_track
from api.serializers import RecommendRequestSerializer


client = APIClient()

# --- Fixtures ---
@pytest.fixture
def seed_track():
    return {
        "track_id": "track123",
        "title": "Bad Guy",
        "artist": "Billie Eilish",
        "artist_mbid": "artist-123",
    }

@pytest.fixture
def candidate_tracks():
    return [
        {
            "id": "t1",
            "title": "Bury a Friend",
            "artist-credit": [{"name": "Billie Eilish", "artist": {"id": "artist-123"}}],
        },
        {
            "id": "t2",
            "title": "You Should See Me in a Crown",
            "artist-credit": [{"name": "Billie Eilish", "artist": {"id": "artist-123"}}],
        },
        {
            "id": "t3",
            "title": "When I Was Older",
            "artist-credit": [{"name": "Billie Eilish", "artist": {"id": "artist-123"}}],
        },
    ]


# --- Tests for /api/recommend/ ---
@patch("api.views.search_musicbrainz_track")
def test_single_recommendation_success(mock_search, seed_track):
    mock_search.return_value = seed_track
    url = reverse("recommend")
    body = {"recent_tracks": ["Bad Guy"], "preferences": {"genre": "pop", "mood": "energetic"}}
    resp = client.post(url, data=json.dumps(body), content_type="application/json")

    assert resp.status_code == 200
    data = resp.json()
    assert data["recommended_track"]["title"] == "Bad Guy"
    assert data["recommended_track"]["artist"] == "Billie Eilish"


def test_single_recommendation_validation_error():
    url = reverse("recommend")
    resp = client.post(url, data=json.dumps({}), content_type="application/json")
    assert resp.status_code in (400, 422)


@patch("api.views.search_musicbrainz_track")
def test_single_recommendation_not_found(mock_search):
    mock_search.return_value = None
    url = reverse("recommend")
    body = {"recent_tracks": ["Nonexistent"]}
    resp = client.post(url, data=json.dumps(body), content_type="application/json")
    assert resp.status_code == 404


# --- Tests for /api/recommend/top/ ---
@patch("api.views.search_musicbrainz_recordings")
@patch("api.views.search_recordings_by_artist_mbid")
@patch("api.views.search_musicbrainz_track")
def test_top5_recommend_success(mock_track, mock_by_mbid, mock_fallback, seed_track, candidate_tracks):
    mock_track.return_value = seed_track
    mock_by_mbid.return_value = candidate_tracks
    mock_fallback.return_value = []

    url = reverse("recommend-top")
    body = {
        "recent_tracks": ["Bad Guy"],
        "preferences": {"artist": "Billie Eilish", "mood": "energetic", "randomize": True, "seed": "42"},
    }
    resp = client.post(url, data=json.dumps(body), content_type="application/json")

    assert resp.status_code == 200
    data = resp.json()
    assert "recommended_tracks" in data
    assert len(data["recommended_tracks"]) <= 5
    assert all("title" in t for t in data["recommended_tracks"])


@patch("api.views.search_musicbrainz_track")
@patch("api.views.search_recordings_by_artist_mbid")
def test_top5_success(mock_by_mbid, mock_track, seed_track, candidate_tracks):
    mock_track.return_value = seed_track
    mock_by_mbid.return_value = candidate_tracks

    url = reverse("recommend-top")
    body = {"recent_tracks": ["Bad Guy"], "preferences": {"artist": "Billie Eilish"}}
    resp = client.post(url, data=json.dumps(body), content_type="application/json")

    assert resp.status_code == 200
    data = resp.json()
    assert "recommended_tracks" in data
    assert len(data["recommended_tracks"]) <= 5
    assert all("title" in t for t in data["recommended_tracks"])

    
@patch("api.views.search_musicbrainz_track")
@patch("api.views.search_recordings_by_artist_mbid")
def test_top5_prioritizes_same_album(mock_by_mbid, mock_track, seed_track, candidate_tracks):
    # Seed track from release group rg1
    seed_track["release-group"] = {"id": "rg1"}
    mock_track.return_value = seed_track
    mock_by_mbid.return_value = candidate_tracks

    url = reverse("recommend-top")
    body = {
        "recent_tracks": ["Bad Guy"],
        "preferences": {"artist": "Billie Eilish"}
    }
    resp = client.post(url, data=json.dumps(body), content_type="application/json")

    assert resp.status_code == 200
    data = resp.json()["recommended_tracks"]

    # ✅ Ensure that a track from the same release-group (rg1) is recommended
    assert any(t["title"] in ["Bury a Friend", "When I Was Older"] for t in data)


@patch("api.views.search_musicbrainz_track")
@patch("api.views.search_recordings_by_artist_mbid")
def test_top5_respects_diversity(mock_by_mbid, mock_track, seed_track):
    seed_track["release-group"] = {"id": "rg1"}
    mock_track.return_value = seed_track

    # Create 5 candidates all from the SAME album + artist
    candidates = [
        {"id": f"t{i}", "title": f"Track{i}", 
         "artist-credit": [{"name": "Billie Eilish"}], 
         "release-group": {"id": "rg1"}}
        for i in range(5)
    ]
    mock_by_mbid.return_value = candidates

    url = reverse("recommend-top")
    body = {"recent_tracks": ["Bad Guy"], "preferences": {"artist": "Billie Eilish"}}
    resp = client.post(url, data=json.dumps(body), content_type="application/json")

    assert resp.status_code == 200
    data = resp.json()["recommended_tracks"]

    # ✅ Should respect diversity: max 3 from same album/artist
    assert len(data) <= 3



def test_search_valid_track():
    result = search_musicbrainz_track("Bad Guy")
    assert result is not None
    assert "title" in result
    assert "artist" in result
    assert "track_id" in result

def test_search_invalid_track():
    result = search_musicbrainz_track("asdfghjkl1234")
    assert result is None

def test_missing_recent_tracks():
    data = {"preferences": {"mood": "happy"}}
    serializer = RecommendRequestSerializer(data=data)
    assert not serializer.is_valid()
    assert "recent_tracks" in serializer.errors

def test_endpoint_with_valid_input():
    url = reverse("recommend")
    body = {"recent_tracks": ["Bad Guy"], "preferences": {"mood": "happy"}}
    response = client.post(url, body, format="json")
    assert response.status_code == 200
    assert "recommended_track" in response.json()
