from pymongo import MongoClient
from transformers import pipeline

# 1. Connect to MongoDB Atlas
client = MongoClient("mongodb+srv://danielarb:m9IeL85JNjFWQR73@cluster0.oz78pty.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["moodmuse"]
collection = db["paintings"]

# 2. Load the emotion classification model
emotion_classifier = pipeline(
    "text-classification",
    model="j-hartmann/emotion-english-distilroberta-base",
    top_k=None
)

# 3. Color → emotion mapping (expanded)
color_emotion_map = {
    "red": ["passion", "anger"],
    "darkred": ["grief", "intensity"],
    "maroon": ["mourning", "memory"],
    "blue": ["calm", "sadness"],
    "navy": ["depth", "melancholy"],
    "skyblue": ["clarity", "freedom"],
    "teal": ["introspection", "renewal"],
    "cyan": ["freshness", "lightness"],
    "green": ["growth", "serenity"],
    "olive": ["wisdom", "groundedness"],
    "lime": ["energy", "youth"],
    "yellow": ["joy", "hope"],
    "gold": ["inspiration", "brilliance"],
    "orange": ["optimism", "vitality"],
    "brown": ["stability", "earthiness"],
    "beige": ["nostalgia", "calm"],
    "pink": ["tenderness", "romance"],
    "hotpink": ["desire", "spontaneity"],
    "purple": ["mystery", "spirituality"],
    "indigo": ["contemplation", "depth"],
    "white": ["purity", "clarity"],
    "black": ["melancholy", "fear"],
    "gray": ["neutrality", "confusion"],
    "silver": ["elegance", "distance"]
}

# 4. Main tagging function
def tag_emotions():
    paintings = list(collection.find({
        "description_blip2": {"$exists": True},
        "color_names": {"$exists": True},
        "emociones": {"$exists": False}
    }))

    for painting in paintings:
        text_emotions = []
        color_emotions = []

        description = painting.get("description_blip2", "")
        color_names = painting.get("color_names", [])

        # Emotions from text
        try:
            result = emotion_classifier(description[:512])[0]
            sorted_emotions = sorted(result, key=lambda x: x["score"], reverse=True)
            text_emotions = [e["label"].lower() for e in sorted_emotions[:3] if e["score"] > 0.3]
        except Exception as e:
            print(f"❌ NLP error on painting {painting.get('objectID')}: {e}")

        # Emotions from color names
        for name in color_names:
            color_emotions.extend(color_emotion_map.get(name.lower(), []))

        # Combine and deduplicate (limit color emotions to 3)
        all_emotions = list(set(text_emotions + color_emotions[:3]))

        # Save to MongoDB
        collection.update_one(
            {"_id": painting["_id"]},
            {"$set": {"emociones": all_emotions}}
        )

        print(f"🎨 Tagged '{painting.get('title', 'Untitled')}' with emotions: {all_emotions}")

# Run it
if __name__ == "__main__":
    tag_emotions()
