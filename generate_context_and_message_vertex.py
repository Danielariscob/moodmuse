from pymongo import MongoClient
import requests
import time
from vertexai.preview.language_models import TextGenerationModel
import vertexai

# 1. Init Vertex AI client
vertexai.init(project="moodmuse", location="us-central1")
model = TextGenerationModel.from_pretrained("text-bison@001")

# 2. Connect to MongoDB
client = MongoClient("mongodb+srv://danielarb:m9IeL85JNjFWQR73@cluster0.oz78pty.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["moodmuse"]
collection = db["paintings"]

# 3. Fetch MET metadata
def fetch_met_metadata(object_id):
    try:
        url = f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{object_id}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"⚠️ MET API error for {object_id}: {e}")
    return {}

# 4. Text generation with Vertex
def generate_text(prompt, max_tokens=200):
    try:
        response = model.predict(prompt=prompt, temperature=0.7, max_output_tokens=max_tokens)
        return response.text.strip()
    except Exception as e:
        print(f"❌ Vertex error: {e}")
        return ""

# 5. Main loop
def enrich_paintings():
    paintings = list(collection.find({
        "analizado_blip2": True,
        "emociones": {"$exists": True},
        "contexto_obra": {"$exists": False}
    }))

    for painting in paintings:
        object_id = painting.get("objectID")
        metadata = fetch_met_metadata(object_id)
        if not metadata:
            continue

        title = painting.get("title", "Untitled")
        artist = metadata.get("artistDisplayName", "Unknown artist")
        date = metadata.get("objectDate", "Unknown date")
        medium = metadata.get("medium") or "unspecified medium"
        culture = metadata.get("culture") or "unspecified cultural context"
        emotion = painting.get("emociones", ["neutral"])[0]

        # Generate context paragraph
        context_prompt = (
            f"Write a short, emotionally resonant but historically accurate paragraph about the painting titled '{title}', "
            f"created by {artist} in {date}. The medium is '{medium}', and the cultural background is '{culture}'. "
            f"Keep it under 100 words and gently informative."
        )
        contexto_obra = generate_text(context_prompt)

        # Generate user message
        message_prompt = (
            f"A user is feeling '{emotion}'. Based on the painting '{title}', write a short, emotionally supportive message (1–2 sentences) "
            f"that helps the user feel understood and connected to the emotional themes of the artwork."
        )
        mensaje_para_usuario = generate_text(message_prompt)

        # Save to MongoDB
        collection.update_one(
            {"_id": painting["_id"]},
            {"$set": {
                "contexto_obra": contexto_obra,
                "mensaje_para_usuario": mensaje_para_usuario
            }}
        )

        print(f"✅ Updated '{title}' with context and message.")

        # Optional: log progress to file
        with open("log.txt", "a", encoding="utf-8") as log:
            log.write(f"{title}: {contexto_obra[:60]}... | {mensaje_para_usuario[:60]}...\n")

        # Optional: polite delay between API calls
        time.sleep(1)

# Run it
if __name__ == "__main__":
    enrich_paintings()
