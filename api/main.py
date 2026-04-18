import os
import sys

# Vercel runs from the api/ directory — add the repo root so `src.*` imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from contextlib import asynccontextmanager
from typing import Dict, Any, List, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.content_model import ContentEngine
from src.hybrid_recommender import HybridRecommender
from src.mood_engine import MoodEngine
from src.user_model import UserModel, generate_synthetic_users

# Global state
app_state: Dict[str, Any] = {}

class SearchQuery(BaseModel):
    query: str

class MoodQuery(BaseModel):
    context: str
    n: int = 10

class UserRecQuery(BaseModel):
    user_id: str
    context: Optional[str] = None
    n: int = 10

class TrackRecQuery(BaseModel):
    track_id: str
    n: int = 15

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Optional startup logic if needed
    yield
    # Cleanup on shutdown
    app_state.clear()


def load_models():
    import os
    is_vercel = os.environ.get("VERCEL") == "1"
    
    # Calculate BASE_DIR relative to api/main.py
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Environment-aware data loading
    if is_vercel:
        # Production (Vercel) - Use 50k sample for serverless stability
        data_path = os.path.join(BASE_DIR, "data", "production_sample.csv")
        subset_size = 50000
    else:
        # Local Development - Use full 1.2M dataset capped at 300k
        data_path = os.path.join(BASE_DIR, "data", "tracks_features.csv")
        subset_size = 300000

    engine = ContentEngine(n_neighbors=200, metric="cosine")
    engine.fit_from_csvs(csv_paths=[data_path], subset=subset_size)

    mood_engine = MoodEngine(engine.scaler)
    user_model = UserModel(recency_halflife=10, like_boost=2.0)
    hybrid = HybridRecommender(
        engine, mood_engine, user_model, alpha=0.45, beta=0.30, gamma=0.25
    )
    users = generate_synthetic_users(engine, mood_engine, n_users=50, tracks_per_user=30)
    
    # Pre-calculate Map Data on Startup
    from src.clustering_viz import reduce_pca
    import numpy as np
    
    sample_size = 5000
    rng = np.random.RandomState(42)
    idxs = rng.choice(len(engine.X), size=min(sample_size, len(engine.X)), replace=False)
    X_sample = engine.X[idxs]
    X_2d, _ = reduce_pca(X_sample, n_components=2)
    moods = mood_engine.batch_assign_moods(X_sample)
    df_sample = engine.df.iloc[idxs]
    
    precalculated_points = []
    for i in range(len(X_2d)):
        precalculated_points.append({
            "x": float(X_2d[i, 0]),
            "y": float(X_2d[i, 1]),
            "mood": moods[i],
            "track_name": df_sample.iloc[i].get("track_name", "Unknown"),
            "artist_name": df_sample.iloc[i].get("artist_name", "Unknown")
        })

    app_state["engine"] = engine
    app_state["mood_engine"] = mood_engine
    app_state["user_model"] = user_model
    app_state["hybrid"] = hybrid
    app_state["users"] = users
    app_state["precalculated_map"] = precalculated_points

def ensure_initialized():
    if "engine" not in app_state:
        load_models()

app = FastAPI(title="SonicSense API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For local Vite development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health_check():
    """Lightweight health check — no model loading."""
    import os, sys
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(base, "data", "production_sample.csv")
    return {
        "alive": True,
        "python": sys.version,
        "cwd": os.getcwd(),
        "base_dir": base,
        "csv_exists": os.path.exists(csv_path),
        "sys_path_0": sys.path[:3],
        "vercel_env": os.environ.get("VERCEL", "not_set"),
    }


@app.get("/api/status")
async def get_status():
    try:
        ensure_initialized()
    except Exception as e:
        import traceback
        return {"error": str(e), "traceback": traceback.format_exc()}
    engine = app_state["engine"]
    users = app_state["users"]
    return {
        "status": "online",
        "catalog_size": engine.catalog_size,
        "feature_dim": engine.feature_dim,
        "listener_profiles": len(users)
    }

@app.post("/api/search")
async def search_tracks(req: SearchQuery):
    ensure_initialized()
    engine = app_state.get("engine")
    if not engine:
        return {"error": "Engine not loaded"}
    
    hits_df = engine.search_tracks(req.query, limit=50)
    hits_df = hits_df.fillna("")
    
    return {"results": hits_df.to_dict(orient="records")}

@app.get("/api/users")
async def get_users():
    ensure_initialized()
    users = app_state.get("users", [])
    return {
        "users": [
            {
                "user_id": u.user_id,
                "preferred_mood": u.preferred_mood,
                "track_count": len(u.all_track_ids)
            } for u in users
        ]
    }

@app.post("/api/recommend/track")
async def recommend_track(req: TrackRecQuery):
    ensure_initialized()
    engine = app_state.get("engine")
    if not engine:
        return {"error": "Engine not loaded"}
    
    try:
        # recommend_by_id returns top N nearest neighbors excluding the seed itself by default
        recs_df = engine.recommend_by_id(req.track_id, n=req.n)
        recs_df = recs_df.fillna("")
        return {"results": recs_df.to_dict(orient="records")}
    except KeyError:
        return {"error": "Track not found in vector space."}

@app.post("/api/recommend/mood")
async def recommend_mood(req: MoodQuery):
    ensure_initialized()
    hybrid = app_state.get("hybrid")
    if not hybrid:
        return {"error": "Engine not loaded"}
    
    recs_df = hybrid.recommend_by_mood(req.context, n=req.n)
    recs_df = recs_df.fillna("")
    return {"results": recs_df.to_dict(orient="records")}

@app.post("/api/recommend/user")
async def recommend_user(req: UserRecQuery):
    ensure_initialized()
    hybrid = app_state.get("hybrid")
    users = app_state.get("users", [])
    if not hybrid:
        return {"error": "Engine not loaded"}
    
    # Find user profile
    user_profile = next((u for u in users if u.user_id == req.user_id), None)
    if not user_profile:
        return {"error": "User not found"}
    
    recs_df = hybrid.recommend_for_user(user_profile, n=req.n, context=req.context)
    recs_df = recs_df.fillna("")
    return {"results": recs_df.to_dict(orient="records")}

@app.get("/api/map")
async def get_map_data():
    ensure_initialized()
    points = app_state.get("precalculated_map")
    if not points:
        return {"error": "Map data not ready"}
    return {"points": points}
