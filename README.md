# 🎧 SonicSense — Elite Music Intelligence Platform

SonicSense is a high-performance, production-grade music recommendation system powered by a massive 1.2M+ track vector space. Designed for precision music discovery, it replaces generic metadata queries with true content-based latent analysis and real-time behavioral modeling.

---

## 💎 The "Deep-Glass" Experience
The platform features an ultra-premium, frameless glass aesthetic with a focus on technical telemetry and spatial visualizations.

| Module | Purpose |
|---|---|
| **Discovery Engine** | Real-time k-NN projection on a 1.2M track manifold. |
| **Mood Matrix** | Centralized orbital radar for resolving contextual moods. |
| **Personal Mixes** | Behavioral centroid modeling with recency-decay weighting. |
| **Sound Map** | Spatial 2D PCA projection of the high-dimensional audio space. |
| **Diagnostics Studio** | Live telemetry monitoring of system latency and RAM pressure. |

---

## 📂 Architecture & Stack

### Core Engine
- **FastAPI Backend**: High-concurrency API handling search indices and ML inference.
- **ML Logic**: Scikit-Learn based `NearestNeighbors` (Cosine Similarity) and `PCA` reduction.
- **Dataset**: `tracks_features.csv` (1.2 Million Rows), optimized for 300K active memory-mapped samples on consumer hardware.

### Frontend Interface
- **React + Vite**: Modern, performant UI with client-side routing.
- **Lucide Icons**: High-fidelity technical iconography.
- **Plotly.js**: Real-time spatial visualizations.
- **Vanilla CSS**: Bespoke "Deep-Glass" design system.

---

## ⚙️ Setup & Deployment

### 1. Backend Environment
```bash
# Enter the root directory
cd Spotify-Music-Recommender

# Setup virtual environment
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Frontend Environment
```bash
cd frontend
npm install
```

### 3. Data Ingestion
Download the `tracks_features.csv` dataset and place it in the `data/` directory. The engine will automatically map the 1.2M tracks upon boot.

---

## 🚀 One-Click Launch
Use the included automation script to boot both the ML engine and the Glass UI simultaneously:
```bash
./start.sh
```
- **Platform URL**: `http://localhost:3000`
- **Engine URL**: `http://localhost:8000`

---

## 🧠 Behavioral Modeling
SonicSense uses **Weighted Behavioral Centroids** to predict your next track.
- **Recency Boost**: Recent listens are exponentialy prioritized over legacy history.
*   **Frequency Amplification**: Repeated interactions deepen the vector gravity.
- **Mood Convergence**: Real-time context hints (Time of Day, User Profile) influence the hybrid scorer.

---

<div align="center">
<sub>Built for the future of music discovery by SonicSense Intelligence</sub>
</div>
