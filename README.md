# SonicSense: High-Dimensional Music Intelligence Platform

SonicSense is a production-grade analytical system designed for large-scale music discovery and latent vector analysis. It utilizes a content-based recommendation architecture projected onto a 1.2M-track coordinate space, providing deep insights into categorical audio features and user behavioral trajectories.

---

## Technical Framework

### 1. Latent Vector Space Ingestion
The system processes a comprehensive dataset of 1.2 Million tracks. Upon boot, the Backend Engine performs the following operations:
- **Heuristic Data Cleaning**: Normalizes artist metadata (removing list literals and bracket noise via regex) and validates high-dimensional feature columns.
- **Dimensionality Optimization**: 
    - **Local Environment**: Currently configured to memory-map a high-diversity subset of **300,000 tracks** (extensible to 1M+ depending on RAM).
    - **Production (Vercel)**: Automatically pivots to a stabilized **50,000-track subset** to ensure the system fits within serverless memory and cold-start constraints.
- **Dependency Management**: To stay within Vercel's 500MB storage limit, the production release is optimized by omitting large deep-learning libraries (e.g., PyTorch) and static plotting tools (Matplotlib), focusing exclusively on the core interactive Scikit-Learn engine.

### 2. Search & Recommendation Logic
SonicSense utilizes a k-Nearest Neighbors (k-NN) algorithm for finding focal points in the music manifold:
- **Metric**: Cosine Similarity.
- **Projection**: The system calculates the inverse cosine distance between the query track's vector and the global manifold, selecting the top 15 nearest entries.
- **Hybrid Scorer**: Fuses content-based vectors with behavioral contexts to refine precision.

### 3. Behavioral Centroid Modeling
The "Personal Mixes" module utilizes a **Recency-Weighted Centroid** approach to profile listening habits:
- **Centroid Calculation**: A user is represented as a single vector point in the music manifold.
- **Exponential Decay**: Recent track interactions contribute significantly more to the user vector than legacy history, allowing the "Mix" to pivot dynamically to current taste.
- **Frequency Weighting**: Repeated plays amplify the "gravity" of specific genres/mood clusters in the user's personal latent space.

### 4. Spatial Projection (PCA)
The Sound Map visualizes the high-dimensional feature set (9D+) using **Principal Component Analysis (PCA)**:
- **Feature Reduction**: Projects the n-dimensional audio landscape onto a 2D plane while preserving global variance.
- **Contextual Clustering**: Tracks are grouped by Mood Engine labels (Chill, Focus, Energetic, etc.), allowing users to see the spatial correlation between raw audio signatures and subjective moods.

---

## Module Overview

### Discovery Engine
The discovery hub uses a dual-pane architecture. The **Source Pane** facilitates focal point selection, while the **Projection Pane** renders calculated latent neighbors. This ensures the user can compare the primary vector to its mathematical neighbors in real-time.

### Mood Matrix
A centralized orbital resolution system. Instead of keyword matching, it maps subjective contexts (e.g., "Late Night," "Gym") to specific audio feature centroids, performing a distance search from those resolved "Golden Vectors."

### Personal Mixes
Provides behavioral telemetry. Users select profile personae to see how specific behavioral centroids (e.g., "Neural Architect") produce unique listening trajectories based on their historical vector movement.

### Diagnostics Studio
The technical command center for monitoring engine health. It reports real-time inference latency (ms), RAM pressure (MB), and the structural integrity of the active KNN index.

---

## Deployment & Execution

### Prerequisites
- **Python 3.10+**: Required for the FastAPI ML engine.
- **Node.js 18+**: Required for the React/Vite interface.
- **Dataset**: `tracks_features.csv` must be located in the `/data` directory.

### Launch Sequence
1. **Repository Calibration**:
   ```bash
   pip install -r requirements.txt
   cd frontend && npm install
   ```

2. **Full System Boot**:
   ```bash
   ./start.sh
   ```
   This script initializes the asynchronous FastAPI lifespan (loading and fitting the manifold) and boots the Vite dev server.

> [!NOTE]
> **Production Context**: The Cloud/Vercel release uses an optimized, serverless-friendly subset of the engine (50k tracks). Deep-learning modules (Autoencoders) and static visualization suites are reserved for the full Local Environment (300k+ tracks) to maintain high-precision real-time response times on the edge.

---

## Architecture Specification
- **Backend**: FastAPI (Python)
- **Frontend**: React 18 / Vite
- **Visuals**: Plotly.js / Lucide
- **Styling**: Deep-Glass Glassmorphism (Vanilla CSS)

---

<div align="center">
SonicSense Intelligence Terminal // Dimensional Discovery Root
</div>
