# 🎵 NextTrack

### Stateless Music Recommendation System

NextTrack is a privacy-focused music recommendation system built with **Django REST Framework**.

Instead of relying on persistent user profiles, listening history, or long-term tracking, NextTrack generates recommendations from the user's **current preferences and context**. It combines music metadata, mood/genre relationships, and heuristic scoring to produce relevant and diverse recommendations.

> **No account. No listening history. No persistent user profile. Just tell NextTrack what you're in the mood for.**

---

## ✨ Features

* 🎯 **Context-based recommendations**

  * Generates recommendations based on the user's current preferences.
  * No long-term user profiling is required.

* 🔒 **Stateless by design**

  * No persistent listening history.
  * No behavioural tracking.
  * Recommendations are generated from the current request.

* 🧠 **Hybrid recommendation algorithm**

  * Combines music metadata.
  * Uses mood-to-genre relationships.
  * Applies heuristic scoring.
  * Ranks recommendation candidates based on relevance.

* 🎲 **Recommendation diversity**

  * Limits repeated artists and albums.
  * Prevents recommendation lists from becoming dominated by a small number of artists.

* 🎨 **Cover artwork**

  * Retrieves album artwork through the **Cover Art Archive** when available.

* 🌐 **REST API**

  * Backend implemented using **Django REST Framework**.
  * Provides structured API endpoints for recommendation requests and responses.

* 🖥️ **Web interface**

  * Responsive frontend built with **Bootstrap** and **Font Awesome**.

* 🧪 **Automated testing**

  * Includes unit and integration tests for core recommendation and API functionality.

---

## 🏗️ Architecture

NextTrack follows an **API-first architecture**:

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
```

---

## 🧠 Recommendation Algorithm

NextTrack uses a **hybrid heuristic recommendation approach** rather than traditional collaborative filtering.

The recommendation pipeline consists of the following stages:

### 1. User Preferences

The system receives the user's current preferences through the API.

These preferences can include contextual information such as:

* Desired mood
* Preferred genre
* Other supported recommendation parameters

### 2. Candidate Generation

Potential tracks are identified using available music metadata and external music information.

### 3. Feature Matching

Candidate tracks are evaluated against the user's requested preferences using:

* Genre relationships
* Mood relationships
* Music metadata
* Other recommendation heuristics

### 4. Candidate Scoring

Each candidate receives a relevance score based on how closely it matches the requested context.

Higher-scoring candidates are considered more relevant to the user's current preferences.

### 5. Diversity Filtering

The recommendation list is filtered to avoid excessive repetition.

For example, the system can limit how many tracks originate from the same:

* Artist
* Album

This creates a more varied recommendation list rather than simply returning the highest-scoring tracks from a single artist.

### 6. Response

The final ranked recommendations are returned through the REST API and displayed by the frontend.

---

## 🔌 External APIs

NextTrack integrates with external music databases to enrich recommendation results.

### MusicBrainz

Used to retrieve music metadata and identify relevant:

* Artists
* Releases
* Recordings

### Cover Art Archive

Used to retrieve album artwork where available.

External API failures are handled gracefully so that unavailable artwork or metadata does not prevent the recommendation system from functioning.

---

## 🛠️ Tech Stack

| Technology                | Purpose                |
| ------------------------- | ---------------------- |
| **Python**                | Core application logic |
| **Django**                | Web framework          |
| **Django REST Framework** | REST API               |
| **SQLite**                | Development database   |
| **HTML / CSS**            | Frontend               |
| **Bootstrap**             | Responsive UI          |
| **Font Awesome**          | UI icons               |
| **MusicBrainz API**       | Music metadata         |
| **Cover Art Archive**     | Album artwork          |
| **pytest**                | Automated testing      |

---

## 🚀 Getting Started

### Prerequisites

Make sure you have the following installed:

* Python 3.x
* pip
* Git

### 1. Clone the Repository

```bash
git clone https://github.com/v1nzD/NextTrack-Project-for-CM3070.git
cd NextTrack-Project-for-CM3070
```

### 2. Create a Virtual Environment

#### Windows

```bash
python -m venv env
env\Scripts\activate
```

#### macOS / Linux

```bash
python3 -m venv env
source env/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply Database Migrations

```bash
python manage.py migrate
```

### 5. Start the Development Server

```bash
python manage.py runserver
```

The application will be available at:

```text
http://127.0.0.1:8000/
```

---

## 🧪 Running Tests

Run the test suite with:

```bash
pytest
```

For more detailed output:

```bash
pytest -v
```

The test suite covers core API and recommendation functionality.

---

## 🔌 API

NextTrack exposes its recommendation functionality through a REST API.

### Recommendation Endpoint

```text
POST /api/...
```

> **Note:** Replace the example endpoint below with the exact endpoint implemented in the project.

### Example Request

```json
{
    "mood": "energetic",
    "genre": "rock"
}
```

### Example Response

```json
{
    "recommendations": [
        {
            "title": "Example Track",
            "artist": "Example Artist",
            "album": "Example Album"
        }
    ]
}
```

---

## 🔐 Privacy

Privacy is one of the core design considerations behind NextTrack.

Traditional recommendation systems often rely on:

* Persistent user profiles
* Listening histories
* Behavioural tracking
* Long-term interaction data

NextTrack instead uses a **stateless recommendation model**.

Recommendations are generated from the user's **current request** without requiring a persistent record of their previous listening behaviour.

This approach reduces the amount of user data that needs to be stored and makes the architecture particularly suitable for applications where **privacy and data minimisation** are important.

---

## 📁 Project Structure

A typical NextTrack project structure is shown below:

```text
NextTrack-Project-for-CM3070/
│
├── manage.py
├── requirements.txt
│
├── <django_project>/
│   ├── settings.py
│   ├── urls.py
│   └── ...
│
├── <application>/
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   ├── tests.py
│   └── ...
│
├── templates/
├── static/
└── README.md
```

> The exact structure may differ depending on the current implementation.

---

## 🎯 Project Goals

NextTrack was designed around three main goals:

1. **Privacy** — provide recommendations without requiring long-term user tracking.
2. **Relevance** — use the user's current mood and preferences to generate useful recommendations.
3. **Diversity** — avoid repetitive recommendation lists dominated by the same artists or albums.

---

## 📌 Project Status

NextTrack was developed as part of the **CM3070 Final Project**.

The project demonstrates the design and implementation of a privacy-focused recommendation system using:

* Django
* Django REST Framework
* External music APIs
* Heuristic recommendation techniques
* Automated testing
* A responsive web interface

---

## 📄 License

This project is intended for **educational and academic purposes** as part of the CM3070 project.

---

## 👤 Author

**v1nzD**

GitHub:
https://github.com/v1nzD/NextTrack-Project-for-CM3070
