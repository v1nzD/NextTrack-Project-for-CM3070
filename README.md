# 🎵 NextTrack

### Stateless Music Recommendation System

NextTrack is a privacy-focused music recommendation system built with **Django REST Framework**.

Instead of relying on persistent user profiles, listening history, or long-term tracking, NextTrack generates recommendations from the user's **current preferences and context**. It combines music metadata, mood/genre relationships, and heuristic scoring to produce relevant and diverse recommendations.

> **No account. No listening history. No persistent user profile. Just tell NextTrack what you're in the mood for.**

---

## ✨ Features

- 🎯 **Context-based recommendations**
  - Generate recommendations from the user's current preferences.
  - No long-term user profiling required.

- 🔒 **Stateless by design**
  - No persistent listening history.
  - No behavioural tracking.
  - Recommendations are generated from the current request.

- 🧠 **Hybrid recommendation algorithm**
  - Combines music metadata
  - Mood-to-genre relationships
  - Heuristic scoring
  - Candidate ranking

- 🎲 **Recommendation diversity**
  - Limits repeated artists and albums.
  - Prevents recommendation lists from becoming dominated by a small number of artists.

- 🎨 **Cover artwork**
  - Retrieves album artwork through the Cover Art Archive when available.

- 🌐 **REST API**
  - Backend implemented using Django REST Framework.
  - Structured API endpoints for recommendation requests and responses.

- 🖥️ **Web interface**
  - Simple responsive frontend built with Bootstrap and Font Awesome.

- 🧪 **Automated testing**
  - Unit and integration tests for core recommendation and API functionality.

---

## 🏗️ Architecture

NextTrack follows an API-first architecture:

```text
                    ┌─────────────────────┐
                    │      Frontend       │
                    │   HTML / Bootstrap  │
                    └──────────┬──────────┘
                               │
                               │ HTTP Request
                               ▼
                    ┌─────────────────────┐
                    │    Django REST API  │
                    │                     │
                    │   Request Handling  │
                    │   Validation        │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Recommendation      │
                    │ Engine              │
                    │                     │
                    │ Metadata            │
                    │ Mood / Genre        │
                    │ Scoring             │
                    │ Diversity Rules     │
                    └──────────┬──────────┘
                               │
                    ┌──────────┴──────────┐
                    ▼                     ▼
          ┌─────────────────┐   ┌─────────────────┐
          │   MusicBrainz   │   │  Cover Art      │
          │      API        │   │    Archive      │
          └─────────────────┘   └─────────────────┘


🧠 Recommendation Algorithm

NextTrack uses a hybrid heuristic recommendation approach rather than a traditional collaborative-filtering model.

The recommendation pipeline broadly follows these stages:

1. User preferences

The system receives the user's current preferences through the API.

These preferences can include contextual information such as desired mood or genre.

2. Candidate generation

Potential tracks are identified using available music metadata and external music information.

3. Feature matching

Candidate tracks are evaluated against the user's requested preferences using:

Genre relationships
Mood relationships
Music metadata
Other recommendation heuristics
4. Candidate scoring

Each candidate receives a relevance score based on how closely it matches the requested context.

5. Diversity filtering

The recommendation list is filtered to avoid excessive repetition.

For example, the system can limit how many tracks originate from the same:

Artist
Album

This creates a more varied recommendation list rather than simply returning the highest-scoring tracks from one artist.

6. Response

The final ranked recommendations are returned through the REST API and displayed by the frontend.

🔌 External APIs

NextTrack integrates with external music databases to enrich recommendation results.

MusicBrainz

Used to retrieve music metadata and identify relevant artists, releases, and recordings.

Cover Art Archive

Used to retrieve album artwork where available.

External API failures are handled so that unavailable artwork or metadata does not prevent the recommendation system from functioning.

🛠️ Tech Stack
Technology	Purpose
Python	Core application logic
Django	Web framework
Django REST Framework	REST API
SQLite	Development database
HTML/CSS	Frontend
Bootstrap	Responsive UI
Font Awesome	UI icons
MusicBrainz API	Music metadata
Cover Art Archive	Album artwork
pytest	Automated testing

🚀 Getting Started
Prerequisites

Make sure you have:

Python 3.x
pip
Git
1. Clone the repository
git clone https://github.com/v1nzD/NextTrack-Project-for-CM3070.git

cd NextTrack-Project-for-CM3070
2. Create a virtual environment
Windows
python -m venv env
env\Scripts\activate
macOS / Linux
python3 -m venv env
source env/bin/activate
3. Install dependencies
pip install -r requirements.txt
4. Apply database migrations
python manage.py migrate
5. Start the development server
python manage.py runserver

The application will then be available at:

http://127.0.0.1:8000/
🧪 Running Tests

Run the test suite with:

pytest

For more detailed output:

pytest -v

The test suite covers the core API and recommendation functionality.

🔌 API

NextTrack exposes its recommendation functionality through a REST API.

Recommendation endpoint
POST /api/...

Example request:

{
    "mood": "energetic",
    "genre": "rock"
}

Example response:

{
    "recommendations": [
        {
            "title": "Example Track",
            "artist": "Example Artist",
            "album": "Example Album"
        }
    ]
}

Note: Replace the example endpoint and request/response fields above with the exact API contract implemented in the project.

🔐 Privacy

Privacy is one of the core design considerations behind NextTrack.

Traditional recommendation systems often rely on:

Persistent user profiles
Listening histories
Behavioural tracking
Long-term interaction data

NextTrack instead uses a stateless recommendation model.

The system can generate recommendations from the user's current request without requiring a persistent record of their previous listening behaviour.

This makes the architecture particularly suitable for applications where minimizing user data collection is important.
