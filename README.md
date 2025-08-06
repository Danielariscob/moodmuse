# 🎨 MoodMuse

**MoodMuse** is an AI-powered web app that connects your emotions with artwork from the Metropolitan Museum of Art (The Met, NYC). Built during the *AI in Action 2025 Hackathon*, MoodMuse combines natural language processing and computer vision to offer a personalized, emotionally resonant museum experience — anytime, anywhere.

## ✨ Features

- ✍️ **Emotion-Based Input**: Write about how you feel (e.g., *"I feel nostalgic and hopeful at the same time"*)
- 🧠 **AI Mood Detection**: The app interprets your emotion using VertexAI's language models
- 🖼️ **Art Recommendation Engine**: Matches you with a painting from The Met’s collection (~15,000+ images)
- 💾 **Save Your Collection**: You can build and revisit your personalized gallery

## 🔧 Tech Stack

- **Frontend**: HTML, JavaScript, Firebase Hosting
- **Backend**: Python, FastAPI (deployed on Google Cloud Run)
- **APIs & Tools**:
  - OpenAI API (for text emotion analysis)
  - BLIP-2 + Vertex AI (for image captioning and computer vision)
  - MongoDB Atlas (dataset enriched with emotional and color metadata)
- **Auth & Database**: Firebase Authentication + Firestore

## 🚀 How to Run Locally

### Prerequisites
- Node.js & npm installed
- Python 3.10+
- Firebase CLI
- OpenAI API key
- Google Cloud credentials
- MongoDB Atlas cluster with paintings dataset

### 1. Clone the repo
```bash
git clone https://github.com/yourusername/moodmuse.git
cd moodmuse
```
### 2. Set up the Backend
```bash
Copiar
Editar
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```
Create a .env file with:
```bash
OPENAI_API_KEY=your_openai_key
MONGO_URI=your_mongodb_uri
```
Run the FastAPI server:
```bash
uvicorn main:app --reload
```
### 3. Set up the Frontend
Update your Firebase config in frontend/index.html.
```bash
cd ../frontend
firebase login
firebase init hosting
firebase deploy
```

## 🌐 Live Demo
Try the app: [MoodMuse Live Demo](https://moodmuse-df2ac.web.app/)

## 🏆 Hackathon Info
This project was built during the AI in Action 2025 Hackathon, organized by Google.
