from pymongo import MongoClient
from PIL import Image
import requests
import torch
from transformers import Blip2Processor, Blip2ForConditionalGeneration
from io import BytesIO
import numpy as np
from collections import Counter
import webcolors

# 1. Connect to MongoDB
client = MongoClient("mongodb+srv://danielarb:m9IeL85JNjFWQR73@cluster0.oz78pty.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["moodmuse"]
collection = db["paintings_subset"]

# Custom color dictionary
CSS3_HEX_TO_NAMES = {
    "#ff0000": "red",
    "#8b0000": "darkred",
    "#800000": "maroon",
    "#0000ff": "blue",
    "#000080": "navy",
    "#87ceeb": "skyblue",
    "#008080": "teal",
    "#00ffff": "cyan",
    "#008000": "green",
    "#808000": "olive",
    "#00ff00": "lime",
    "#ffff00": "yellow",
    "#ffd700": "gold",
    "#ffa500": "orange",
    "#a52a2a": "brown",
    "#f5f5dc": "beige",
    "#ffc0cb": "pink",
    "#ff69b4": "hotpink",
    "#800080": "purple",
    "#4b0082": "indigo",
    "#ffffff": "white",
    "#000000": "black",
    "#808080": "gray",
    "#c0c0c0": "silver",
}

# 2. Load BLIP-2
device = "cuda" if torch.cuda.is_available() else "cpu"
processor = Blip2Processor.from_pretrained("Salesforce/blip2-opt-2.7b", device_map="auto")
model = Blip2ForConditionalGeneration.from_pretrained(
    "Salesforce/blip2-opt-2.7b",
    torch_dtype=torch.float16 if device == "cuda" else torch.float32,
    device_map="auto"
)
#model.to(device)

# 3. Find closest color name from RGB
def closest_color_name(rgb):
    min_colors = {}
    for hex_code, name in CSS3_HEX_TO_NAMES.items():
        r_c, g_c, b_c = webcolors.hex_to_rgb(hex_code)
        rd = (r_c - rgb[0]) ** 2
        gd = (g_c - rgb[1]) ** 2
        bd = (b_c - rgb[2]) ** 2
        min_colors[(rd + gd + bd)] = name
    return min_colors[min(min_colors.keys())]

# 4. Get dominant RGB colors and their names
def get_colors(image, num_colors=5):
    image = image.resize((100, 100))
    arr = np.array(image).reshape(-1, 3)
    color_counts = Counter([tuple(pixel) for pixel in arr])
    most_common = color_counts.most_common(num_colors)

    colors_rgb = [list(color[0]) for color in most_common]
    color_names = [closest_color_name(color[0]) for color in most_common]

    return {
        "rgb": colors_rgb,
        "names": color_names
    }

# 5. Process paintings
def analyze_paintings_with_blip2():
    paintings = list(collection.find({"analizado_blip2": {"$ne": True}}))

    for painting in paintings:
        try:
            image_url = painting.get("primaryImageSmall")
            if not image_url:
                continue

            response = requests.get(image_url)
            image = Image.open(BytesIO(response.content)).convert("RGB")

            # Generate image description
            inputs = processor(
                images=image,
                text="Describe this painting in detail.",
                return_tensors="pt"
            ).to(device, torch.float16 if device == "cuda" else torch.float32)

            generated_ids = model.generate(**inputs, max_new_tokens=100)
            generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0].strip()

            # Get color data
            color_data = get_colors(image)

            # Update MongoDB
            collection.update_one(
                {"objectID": painting["objectID"]},
                {"$set": {
                    "description_blip2": generated_text,
                    "dominant_colors": color_data["rgb"],
                    "color_names": color_data["names"],
                    "analizado_blip2": True
                }}
            )

            print(f"✅ '{painting['title']}' updated with description and colors.")

        except Exception as e:
            print(f"❌ Error in '{painting.get('title', 'Untitled')}': {e}")

# Run the script
if __name__ == "__main__":
    analyze_paintings_with_blip2()
