from flask import Flask, render_template, request
import csv
import random
import os

app = Flask(__name__)

# ==========================================
# LOAD MOVIES DATASET (SAFE FOR RENDER)
# ==========================================
def load_movies():
    movies = []

    try:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(BASE_DIR, "movies_cleaned.csv")

        with open(csv_path, encoding="utf-8") as file:
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

    except Exception as e:
        print("❌ Error loading CSV:", e)

    print("✅ Total Movies Loaded:", len(movies))
    return movies


ALL_MOVIES = load_movies()

# ==========================================
# FACE EMOTION → MOOD MAPPING
# ==========================================
def map_face_emotion(emotion):
    if not emotion:
        return "happy"

    emotion = emotion.lower()

    emotion_map = {
        "happy": "happy",
        "surprised": "happy",
        "sad": "sad",
        "fear": "scary",
        "angry": "scary",
        "disgust": "scary",
        "neutral": "relaxed"
    }

    return emotion_map.get(emotion, "happy")


# ==========================================
# MOVIE FILTERING
# ==========================================
def get_movies_by_mood(mood):
    if not ALL_MOVIES:
        return []

    mood = mood.lower()

    if mood == "sad":
        filtered = [m for m in ALL_MOVIES if "drama" in m["genre"].lower()]
    elif mood == "happy":
        filtered = [m for m in ALL_MOVIES if "comedy" in m["genre"].lower()]
    elif mood == "scary":
        filtered = [m for m in ALL_MOVIES if "horror" in m["genre"].lower() or "thriller" in m["genre"].lower()]
    else:
        filtered = ALL_MOVIES

    if not filtered:
        filtered = ALL_MOVIES

    random.shuffle(filtered)
    return filtered[:50]


# ==========================================
# ROUTES
# ==========================================
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/recommend", methods=["GET", "POST"])
def recommend():
    emotion = request.values.get("emotion", "happy")

    mood = map_face_emotion(emotion)
    movies = get_movies_by_mood(mood)

    print("Emotion:", emotion, "| Mood:", mood, "| Movies:", len(movies))

    return render_template("movies.html", mood=mood.capitalize(), movies=movies)


# ==========================================
# RUN APP (RENDER READY)
# ==========================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
