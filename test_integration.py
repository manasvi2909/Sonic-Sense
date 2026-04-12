#!/usr/bin/env python3
"""
Integration Test — Music Intelligence System
=============================================
End-to-end pipeline test that validates every module works together:
  1. Load dataset & fit ContentEngine
  2. Initialise MoodEngine & verify mood assignment
  3. Generate synthetic users via UserModel
  4. Train Autoencoder & verify embeddings
  5. Run HybridRecommender in all modes
  6. Run full evaluation suite
  7. Generate clustering visualisation
  8. Verify explainability output

Run:
    python test_integration.py
"""

from __future__ import annotations

import sys
import time
import traceback
from pathlib import Path

import numpy as np
import pandas as pd


def section(title: str) -> None:
    print(f"\n{'━' * 60}")
    print(f"  {title}")
    print(f"{'━' * 60}")


def main() -> None:
    t0 = time.time()
    errors = []

    # ── 1. Content Engine ────────────────────────────────────────────────
    section("1 │ Content Engine")
    try:
        from src.content_model import ContentEngine

        engine = ContentEngine(n_neighbors=200, metric="cosine")
        engine.fit_from_csvs(data_dir="data")
        print(f"  ✔ Loaded {engine.catalog_size:,} tracks, {engine.feature_dim}D features")

        # Quick recommendation test
        sample_id = engine.df.iloc[0]["track_id"]
        recs = engine.recommend_by_id(sample_id, n=5)
        assert len(recs) == 5, f"Expected 5 recs, got {len(recs)}"
        assert all(0 <= s <= 1 for s in recs["similarity"]), "Similarity out of range"
        print(f"  ✔ Single-seed recs: {len(recs)} tracks, sims {recs['similarity'].min():.3f}–{recs['similarity'].max():.3f}")

        # Multi-seed
        multi_ids = engine.df.iloc[:3]["track_id"].tolist()
        recs_multi = engine.recommend_from_multiple(multi_ids, n=5)
        assert len(recs_multi) == 5
        print(f"  ✔ Multi-seed recs: {len(recs_multi)} tracks")

        # Search
        results = engine.search_tracks("ed sheeran", limit=5)
        print(f"  ✔ Search 'ed sheeran': {len(results)} results")

        # Vector retrieval
        vec = engine.get_track_vector(sample_id)
        assert vec.shape == (engine.feature_dim,)
        print(f"  ✔ Vector shape: {vec.shape}")

    except Exception as e:
        errors.append(("Content Engine", e))
        traceback.print_exc()

    # ── 2. Mood Engine ───────────────────────────────────────────────────
    section("2 │ Mood Engine")
    try:
        from src.mood_engine import MoodEngine, MOOD_NAMES

        mood_engine = MoodEngine(engine.scaler)

        # Single assignment
        mood = mood_engine.assign_mood(engine.X[0])
        assert mood in MOOD_NAMES
        print(f"  ✔ Track 0 mood: {mood}")

        # Batch assignment
        all_moods = mood_engine.batch_assign_moods(engine.X)
        mood_dist = {m: np.sum(all_moods == m) for m in MOOD_NAMES}
        print(f"  ✔ Mood distribution: {mood_dist}")

        # Context mapping
        test_contexts = ["gym", "study", "breakup", "late night", "date night"]
        for ctx in test_contexts:
            m = mood_engine.context_to_mood(ctx)
            print(f"    '{ctx}' → {m}")
        print("  ✔ All context mappings resolved")

        # Mood similarity
        mv = mood_engine.context_to_mood_vector("gym")
        sim = mood_engine.mood_similarity(engine.X[0], mv)
        print(f"  ✔ Track 0 ↔ 'gym' similarity: {sim:.4f}")

    except Exception as e:
        errors.append(("Mood Engine", e))
        traceback.print_exc()

    # ── 3. User Model ───────────────────────────────────────────────────
    section("3 │ User Model & Synthetic Users")
    try:
        from src.user_model import UserModel, generate_synthetic_users

        users = generate_synthetic_users(engine, mood_engine, n_users=20, tracks_per_user=25)
        print(f"  ✔ Generated {len(users)} synthetic users")
        print(f"    User 0: {users[0].user_id}, {len(users[0].all_track_ids)} tracks, mood={users[0].preferred_mood}")

        user_model = UserModel(recency_halflife=10, like_boost=2.0)
        user_vec = user_model.build_user_vector(users[0], engine)
        assert user_vec.shape == (engine.feature_dim,)
        print(f"  ✔ User vector shape: {user_vec.shape}")

        # Time context
        if users[0].timestamps:
            bucket, hint = user_model.infer_time_context(users[0].timestamps)
            print(f"  ✔ Time context: {bucket} → mood hint: {hint}")

        # Preferred mood
        pref = user_model.get_preferred_mood(users[0], engine, mood_engine)
        print(f"  ✔ Preferred mood: {pref}")

    except Exception as e:
        errors.append(("User Model", e))
        traceback.print_exc()

    # ── 4. Autoencoder ───────────────────────────────────────────────────
    section("4 │ Autoencoder Embeddings")
    try:
        from src.autoencoder import AutoencoderTrainer

        trainer = AutoencoderTrainer(
            latent_dim=16, noise_std=0.1,
            lr=1e-3, epochs=20, batch_size=512,
        )
        print("  Training autoencoder (20 epochs for test)...")
        trainer.train(engine, verbose=True)

        # Encode full catalog
        embeddings = trainer.encode_catalog(engine)
        assert embeddings.shape == (engine.catalog_size, 16)
        print(f"  ✔ Embedding matrix: {embeddings.shape}")

        # Reconstruction error
        recon_err = trainer.reconstruction_error(engine)
        print(f"  ✔ Reconstruction MSE: {recon_err:.6f}")

        # Save/load cycle
        ckpt_path = "data/autoencoder_test.pt"
        trainer.save(ckpt_path)
        trainer2 = AutoencoderTrainer(latent_dim=16)
        trainer2.load(ckpt_path)
        emb2 = trainer2.encode_catalog(engine)
        assert np.allclose(embeddings, emb2, atol=1e-5)
        print("  ✔ Save/load round-trip OK")

        # Clean up
        Path(ckpt_path).unlink(missing_ok=True)

    except ImportError as e:
        print(f"  ⚠ PyTorch not installed, skipping autoencoder: {e}")
    except Exception as e:
        errors.append(("Autoencoder", e))
        traceback.print_exc()

    # ── 5. Hybrid Recommender ────────────────────────────────────────────
    section("5 │ Hybrid Recommender")
    try:
        from src.hybrid_recommender import HybridRecommender

        hybrid = HybridRecommender(
            engine, mood_engine, user_model,
            alpha=0.45, beta=0.30, gamma=0.25,
        )
        print(f"  {hybrid}")

        # Full hybrid
        seed = engine.df.iloc[0]["track_id"]
        recs = hybrid.recommend(
            seed_ids=[seed], user_profile=users[0], context="gym", n=10
        )
        assert len(recs) == 10
        assert "explanation" in recs.columns
        print(f"  ✔ Full hybrid: {len(recs)} recs")
        print(f"    Top rec: {recs.iloc[0]['track_name']} — score {recs.iloc[0]['hybrid_score']:.4f}")
        print(f"    Explanation: {recs.iloc[0]['explanation']}")

        # Mood-only
        mood_recs = hybrid.recommend_by_mood("study", n=5)
        assert len(mood_recs) == 5
        print(f"  ✔ Mood-only ('study'): {len(mood_recs)} recs")

        # User-only
        user_recs = hybrid.recommend_for_user(users[0], n=5)
        assert len(user_recs) == 5
        print(f"  ✔ User-only: {len(user_recs)} recs")

        # Content-only
        content_recs = hybrid.recommend_content_only([seed], n=5)
        assert len(content_recs) == 5
        print(f"  ✔ Content-only: {len(content_recs)} recs")

    except Exception as e:
        errors.append(("Hybrid Recommender", e))
        traceback.print_exc()

    # ── 6. Evaluation ────────────────────────────────────────────────────
    section("6 │ Evaluation Suite")
    try:
        from src.evaluation import Evaluator

        evaluator = Evaluator(engine)

        # Single list
        single_eval = evaluator.evaluate_single_list(recs)
        print(f"  ✔ Single list: ILD={single_eval['intra_list_diversity']:.4f}, novelty={single_eval['novelty']:.4f}")

        # Full evaluation
        full_results = evaluator.full_evaluation(
            hybrid, users[:10], k=10, context="gym", verbose=False
        )
        evaluator.print_evaluation_report(full_results)

    except Exception as e:
        errors.append(("Evaluation", e))
        traceback.print_exc()

    # ── 7. Clustering & Visualisation ────────────────────────────────────
    section("7 │ Clustering & Visualization")
    try:
        from src.clustering_viz import (
            cluster_tracks_kmeans, reduce_pca, plot_music_space, find_optimal_k,
        )

        # KMeans
        labels, sil, _ = cluster_tracks_kmeans(engine.X, n_clusters=5)
        print(f"  ✔ KMeans(k=5): silhouette={sil:.4f}")

        # Optimal k search (small range for speed)
        best_k, k_scores = find_optimal_k(engine.X, k_range=range(3, 8))
        print(f"  ✔ Best k={best_k} (scores: {k_scores})")

        # PCA
        X_2d, pca_model = reduce_pca(engine.X, n_components=2)
        print(f"  ✔ PCA: explained variance = {pca_model.explained_variance_ratio_.sum():.3f}")

        # Plot with mood labels
        mood_labels = mood_engine.batch_assign_moods(engine.X)
        fig = plot_music_space(
            X_2d, mood_labels, label_type="mood",
            title="Music Space (PCA, Mood-coloured)",
            save_path="data/music_space_pca.png",
        )
        print("  ✔ Plot saved → data/music_space_pca.png")

    except Exception as e:
        errors.append(("Clustering/Viz", e))
        traceback.print_exc()

    # ── 8. Explainability ────────────────────────────────────────────────
    section("8 │ Explainability")
    try:
        from src.explainability import explain_recommendation_detailed, feature_contribution_breakdown
        from src.content_model import AUDIO_FEATURES

        seed_id = engine.df.iloc[0]["track_id"]
        rec_id = engine.df.iloc[1]["track_id"]

        detail = explain_recommendation_detailed(seed_id, rec_id, engine, mood_engine)
        print(f"  ✔ Seed mood: {detail['seed_mood']}, Rec mood: {detail['rec_mood']}, match: {detail['mood_match']}")
        print(f"  ✔ Top features: {detail['top_features']}")

        # Feature breakdown
        sv = engine.get_track_vector(seed_id)
        rv = engine.get_track_vector(rec_id)
        contribs = feature_contribution_breakdown(sv, rv, AUDIO_FEATURES)
        top_3 = sorted(contribs, key=contribs.get, reverse=True)[:3]
        print(f"  ✔ Top-3 contributing features: {top_3}")
        print(f"    Contributions: {[f'{k}={contribs[k]:.4f}' for k in top_3]}")

    except Exception as e:
        errors.append(("Explainability", e))
        traceback.print_exc()

    # ── Summary ──────────────────────────────────────────────────────────
    elapsed = time.time() - t0
    section("Summary")
    if errors:
        print(f"  ❌ {len(errors)} module(s) failed:")
        for name, err in errors:
            print(f"     • {name}: {err}")
        sys.exit(1)
    else:
        print(f"  ✅ All 8 modules passed! ({elapsed:.1f}s)")
        sys.exit(0)


if __name__ == "__main__":
    main()
