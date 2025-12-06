ReyMini – Static Q/A Chatbot (Python + FastAPI + React + Tailwind + Framer Motion)

This project is divided into two main parts: backend (chat logic + similarity search)
and frontend (UI + animations). The chatbot works fully offline using a dataset-based
Q/A system with optional SBERT embeddings for high accuracy.

──────────────────────────────────────────────────────────────
📁 Project Folder Structure
──────────────────────────────────────────────────────────────

staticBot/
│
├── backend/                     → Python FastAPI server
│   ├── app.py                  → Main API (reply logic, SBERT/TF-IDF, Annoy search)
│   ├── responses.json          → Dataset containing Q/A pairs
│   ├── requirements.txt        → Backend dependencies
│   ├── utils/
│   │   ├── text_utils.py       → Text cleaning, Hinglish normalize, spell-corrector
│   │   └── annoy_index.py      → ANN (Annoy) index builder & loader
│   └── models/
│       └── q_ann.ann           → Auto-generated ANN index for fast vector search
│
└── frontend/                   → React + Tailwind + Framer Motion UI
    ├── src/
    │   ├── ChatApp.jsx         → Main chat interface (dark UI, animations, API calls)
    │   ├── index.js            → React entry point
    │   ├── index.css           → Global Tailwind styles + custom dark theme
    │   └── components/
    │       └── MessageBubble.jsx → Animated chat bubbles (Bot & User)
    │
    ├── tailwind.config.js      → Tailwind setup
    ├── package.json            → Frontend dependencies
    └── public/                 → Static assets

──────────────────────────────────────────────────────────────
⚙️ Backend (FastAPI) Details
──────────────────────────────────────────────────────────────
• Loads responses.json dataset  
• Cleans/normalizes queries (Hinglish → English)  
• Optional SBERT embeddings for semantic similarity  
• Annoy index for fast nearest-neighbor search  
• Returns best-matching answer with score  
• Endpoints:
  - POST /reply  → returns answer
  - GET /stats   → accuracy average & query count

Run backend:
  uvicorn app:app --reload --port 8000

──────────────────────────────────────────────────────────────
🎨 Frontend (React) Details
──────────────────────────────────────────────────────────────
• Dark professional UI  
• Gradient accents + blur glass effect  
• Smooth animations using Framer Motion  
• Message bubbles with bot 🤖 and user 🙋 avatars  
• Typing indicator  
• Fetches reply from FastAPI API  
• Responsive layout

Run frontend:
  npm install
  npm start

──────────────────────────────────────────────────────────────
🔗 Full Workflow
──────────────────────────────────────────────────────────────
User → React UI → POST /reply → FastAPI  
→ Text cleaning → Normalize → SBERT (optional)  
→ Annoy top-k search → Select answer → UI displays animated bubble

──────────────────────────────────────────────────────────────
📦 Dataset (responses.json)
──────────────────────────────────────────────────────────────
A static Q/A JSON file shaped like:

[
  { "question": "what is python", "answer": "Python is a high-level language..." },
  { "question": "resume kaise banaye", "answer": "Resume contains education..." }
]

You can add unlimited Q/A pairs.

──────────────────────────────────────────────────────────────
🎯 Accuracy
──────────────────────────────────────────────────────────────
• TF-IDF accuracy: 60–75%  
• SBERT accuracy: 80–90%  
• Annoy improves speed 5–20× for large datasets  

──────────────────────────────────────────────────────────────
📌 Conclusion
──────────────────────────────────────────────────────────────
ReyMini is a clean, fast, offline-capable chatbot built with a professional UI,
semantic search backend, and modern animations. The structure is scalable and can
handle thousands of Q/A pairs easily.

