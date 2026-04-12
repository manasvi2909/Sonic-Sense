# 🎧 SonicSense — Intelligent Music Discovery

A context-aware **Music Recommendation System** built with the [Spotify Audio Features dataset](https://www.kaggle.com/datasets/tomigelo/spotify-audio-features).  
SonicSense combines **content-based filtering**, **mood-context mapping**, **user behavioral modeling**, and **autoencoder-based latent embeddings** into a hybrid recommendation engine — with a premium Streamlit frontend for real-time interaction.

---

## ✨ Key Features

| Module | Description |
|---|---|
| **Content Engine** | k-NN search on scaled audio features (cosine similarity) |
| **Mood Matrix** | Automated mood classification + context-to-mood resolver |
| **User Modeling** | Recency-weighted behavioral profiles with temporal awareness |
| **Hybrid Scorer** | α·content + β·user + γ·mood fusion with explainability |
| **Autoencoder** | Latent representation learning for improved distance metrics |
| **Evaluation Suite** | Diversity, novelty, personalization, coverage, NDCG, hit-rate |
| **Explainability** | Per-recommendation feature-contribution breakdowns |

---

## 📂 Project Structure

```
SonicSense/
├── app/
│   ├── streamlit_app.py      # Main Streamlit application
│   ├── pages.py              # Page renderers (Dashboard, Scan, Mood, etc.)
│   └── retro_theme.py        # Premium UI theme system
├── src/
│   ├── content_model.py      # Content-based engine (k-NN)
│   ├── mood_engine.py        # Mood classification & context mapping
│   ├── user_model.py         # User behavioral modeling
│   ├── hybrid_recommender.py # Hybrid recommendation scorer
│   ├── autoencoder.py        # Autoencoder for latent embeddings
│   ├── clustering_viz.py     # PCA / dimensionality reduction
│   ├── evaluation.py         # Recommendation quality metrics
│   ├── explainability.py     # Feature contribution explanations
│   └── api_integration.py    # Spotify API scaffold
├── data/                     # CSV datasets
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup

1. **Clone & enter**:
   ```bash
   git clone https://github.com/yourusername/spotify-recommender.git
   cd spotify-recommender
   ```

2. **Create environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   pip install streamlit plotly
   ```

3. **Download dataset** from [Kaggle](https://www.kaggle.com/datasets/tomigelo/spotify-audio-features) and place CSVs in `data/`.

---

## 🚀 Launch

### Streamlit UI (recommended)

```bash
streamlit run app/streamlit_app.py
```

This launches the full SonicSense experience with:
- **Dashboard** — system overview, mood distribution, status
- **Track Scan** — search, fingerprint, and get recommendations
- **Mood Matrix** — context-aware mood discovery
- **User Profile** — behavioral modeling & personalized discovery
- **Music Space** — PCA visualization of the feature landscape
- **Diagnostics** — evaluation metrics & quality assessment
- **Deep Scan** — side-by-side track comparison & analysis

### CLI (quick recommendations)

```bash
python offline_recommender.py --csv data/SpotifyAudioFeaturesApril2019.csv --seed-query "shape of you" --top 15
```

---

## 🧠 How it Works

1. Extracts key **audio features** (`danceability`, `energy`, `tempo`, etc.)
2. Scales features with `StandardScaler`
3. Uses `NearestNeighbors` (cosine similarity) for content-based retrieval
4. **Mood Engine** classifies tracks into 5 mood categories with context resolution
5. **User Model** builds recency-weighted preference vectors from listening history
6. **Hybrid Scorer** fuses content, user, and mood signals: `α·content + β·user + γ·mood`
7. **Explainability** module provides per-recommendation feature contribution breakdowns

---

## 📊 Evaluation Metrics

| Metric | Description |
|---|---|
| **Hit-Rate@K** | Fraction of test cases where a same-artist track is in the top-K |
| **NDCG@K** | Normalized discounted cumulative gain |
| **Intra-list Diversity** | Average pairwise distance within recommendation lists |
| **Novelty** | Information-theoretic surprise measure |
| **Personalization** | Uniqueness across different user recommendation lists |
| **Coverage** | Fraction of catalog represented across all recommendations |

---

## 🔮 Future Roadmap

- [ ] Live Spotify Web API integration for real-time playlists
- [ ] Autoencoder-trained latent embeddings for enhanced retrieval
- [ ] Collaborative filtering hybrid layer
- [ ] Playlist generation with transition smoothing
- [ ] User authentication & persistent profiles

---

<div align="center">
<sub>Built with ♬ by SonicSense</sub>
</div>
