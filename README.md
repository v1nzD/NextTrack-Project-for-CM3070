# NextTrack-Project-for-CM3070
CM3070 Final Project - NextTrack Music Recommendation API

# 🎵 NextTrack – Stateless Music Recommendation System

NextTrack is my **Final Year Project (CM3070 – Artificial Intelligence)**, designed as a **stateless music recommendation system**.  
Unlike conventional recommenders that rely on heavy user profiling and long-term tracking, NextTrack emphasizes **privacy, contextual immediacy, and short-term preference-based recommendations**.

---

## 🚀 Features
- **Stateless Recommendations**: No persistent user tracking or history required.  
- **Hybrid Algorithm**: Combines metadata analysis, mood–genre mapping, and scoring heuristics.  
- **Diversity Constraints**: Prevents repetitive results by limiting tracks from the same artist/album.  
- **Cover Art Integration**: Fetches album art from the Cover Art Archive (when available).  
- **Modern UI**: Simple, professional frontend with Bootstrap + FontAwesome.  
- **API-first Design**: Backend powered by Django REST Framework (DRF).  

---

## 📂 Project Structure
nexttrack_project/
│── api/ # Core Django app
│ ├── views.py # Recommendation logic
│ ├── serializers.py # API input/output validation
│ ├── musicbrainz.py # External MusicBrainz integration
│ └── tests/ # Unit & integration tests
│
│── templates/ # Frontend (home.html, etc.)
│
├── manage.py # Django entry point
├── requirements.txt # Dependencies
└── README.md # Project documentation

## How to run the app
1. Create and activate a virtual environment:

python -m venv env
# On Windows (PowerShell):
env\Scripts\activate
# On macOS/Linux:
source env/bin/activate

2. Install Dependencies:

pip install -r requirements.txt

3. Run database migrations:

python manage.py migrate

4. Start development server:

python manage.py runserver

