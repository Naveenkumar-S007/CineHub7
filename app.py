from flask import Flask, render_template, request
import csv
import random
from emotion_detector import detect_face_emotion  # NEW

app = Flask(__name__)

# ==========================================
# Load Movies Dataset
# ==========================================
def load_movies():
    movies = []

    try:
        with open("movies_cleaned.csv", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row in reader:
                title = row.get("Movie_Title", "").strip()

                if not title:
                    continue

                movies.append({
                    "title": title,
                    "genre": f"{row.get('main_genre', '')}, {row.get('side_genre', '')}",
                    "director": row.get("Director", ""),
                    "cast": row.get("Actors", ""),
                    "poster_url": row.get("poster_url", "/static/images/default.jpg"),
                    "imdb_rating": row.get("Rating", "N/A"),
                    "year": row.get("Year", ""),
                    "imdb_link": f"https://www.imdb.com/find?q={title}",
                    "trailer_link": f"https://www.youtube.com/results?search_query={title}+official+trailer",
                    "ott_link": f"https://www.justwatch.com/in/search?q={title}"
                })

    except FileNotFoundError:
        print("❌ movies_cleaned.csv not found.")

    print("✅ Total Movies Loaded:", len(movies))
    return movies


ALL_MOVIES = load_movies()

# ==========================================
# TEXT Emotion Detection
# ==========================================
def detect_emotion(text):
    text = text.lower()

    if any(word in text for word in ["sad", "depressed", "heartbroken"]):
        return "sad"
    elif any(word in text for word in ["happy", "excited", "joy", "cheerful"]):
        return "happy"
    elif any(word in text for word in ["scared", "fear", "horror", "terrified"]):
        return "scary"
    elif "bored" in text:
        return "bored"
    elif any(word in text for word in ["relaxed", "calm", "peaceful"]):
        return "relaxed"
    else:
        return "happy"


# ==========================================
# FACE Emotion Mapping
# ==========================================
def map_face_emotion(emotion):
    emotion = emotion.lower()
    if emotion == "happy":
        return "happy"
    elif emotion == "sad":
        return "sad"
    elif emotion in ["fear", "angry", "scary"]:
        return "scary"
    elif emotion == "neutral":
        return "relaxed"
    else:
        return "happy"


# ==========================================
# Mood Based Filtering
# ==========================================
def get_movies_by_mood(mood):
    if not ALL_MOVIES:
        return []

    if mood == "sad":
        filtered = [m for m in ALL_MOVIES if "Drama" in m["genre"]]
    elif mood == "happy":
        filtered = [m for m in ALL_MOVIES if "Comedy" in m["genre"]]
    elif mood == "scary":
        filtered = [m for m in ALL_MOVIES if "Thriller" in m["genre"] or "Horror" in m["genre"]]
    else:
        filtered = ALL_MOVIES.copy()

    if not filtered:
        filtered = ALL_MOVIES.copy()

    random.shuffle(filtered)
    return filtered[:50]


# ==========================================
# Routes
# ==========================================
@app.route("/")
def home():
    return render_template("index.html")


# TEXT & CAMERA emotion recommendation
@app.route('/recommend', methods=['GET', 'POST'])
def recommend():
    # ✅ Detect method
    if request.method == 'POST':
        emotion = request.form.get('emotion')
    else:
        emotion = request.args.get('emotion')

    print("Emotion received:", emotion)

    if not emotion:
        emotion = "happy"

    mood = map_face_emotion(emotion)
    movies = get_movies_by_mood(mood)

    return render_template("movies.html", mood=mood.capitalize(), movies=movies)


# FACE emotion recommendation (optional route)
@app.route("/detect_face")
def detect_face():
    face_emotion = detect_face_emotion()
    mood = map_face_emotion(face_emotion)
    movies = get_movies_by_mood(mood)
    return render_template("movies.html", mood=mood.capitalize(), movies=movies)


# ==========================================
# Run App
# ==========================================
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
