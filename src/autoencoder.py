"""
Autoencoder Embedding Upgrade
==============================
Replaces (or augments) raw Spotify audio features with learned latent
embeddings via a de-noising autoencoder.

Architecture
------------
  Input (9 features, scaled) →
    Encoder: 9 → 128 → 64 → 32 →  **latent (16-D)** →
    Decoder: 16 → 32 → 64 → 128 → 9

Training adds Gaussian noise (σ=0.1) to the input to learn robust
representations (denoising autoencoder).

After training, the encoder is used to project all tracks into a 16-D
embedding space that captures non-linear feature interactions the raw
cosine distance misses.

The ContentEngine can optionally swap its feature matrix for these
embeddings (or concatenate them with the raw features).
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Tuple

import numpy as np

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import DataLoader, TensorDataset
    _TORCH_AVAILABLE = True
except ImportError:
    _TORCH_AVAILABLE = False

from .content_model import ContentEngine


# ── Network Definition ───────────────────────────────────────────────────────

if _TORCH_AVAILABLE:

    class _Encoder(nn.Module):
        def __init__(self, input_dim: int, latent_dim: int) -> None:
            super().__init__()
            self.net = nn.Sequential(
                nn.Linear(input_dim, 128),
                nn.BatchNorm1d(128),
                nn.LeakyReLU(0.2),
                nn.Dropout(0.2),
                nn.Linear(128, 64),
                nn.BatchNorm1d(64),
                nn.LeakyReLU(0.2),
                nn.Dropout(0.1),
                nn.Linear(64, 32),
                nn.BatchNorm1d(32),
                nn.LeakyReLU(0.2),
                nn.Linear(32, latent_dim),
            )

        def forward(self, x: "torch.Tensor") -> "torch.Tensor":
            return self.net(x)

    class _Decoder(nn.Module):
        def __init__(self, latent_dim: int, output_dim: int) -> None:
            super().__init__()
            self.net = nn.Sequential(
                nn.Linear(latent_dim, 32),
                nn.BatchNorm1d(32),
                nn.LeakyReLU(0.2),
                nn.Dropout(0.1),
                nn.Linear(32, 64),
                nn.BatchNorm1d(64),
                nn.LeakyReLU(0.2),
                nn.Dropout(0.2),
                nn.Linear(64, 128),
                nn.BatchNorm1d(128),
                nn.LeakyReLU(0.2),
                nn.Linear(128, output_dim),
            )

        def forward(self, z: "torch.Tensor") -> "torch.Tensor":
            return self.net(z)

    class MusicAutoencoder(nn.Module):
        """Denoising autoencoder for Spotify audio features."""

        def __init__(
            self,
            input_dim: int = 9,
            latent_dim: int = 16,
            noise_std: float = 0.1,
        ) -> None:
            super().__init__()
            self.input_dim = input_dim
            self.latent_dim = latent_dim
            self.noise_std = noise_std
            self.encoder = _Encoder(input_dim, latent_dim)
            self.decoder = _Decoder(latent_dim, input_dim)

        def add_noise(self, x: "torch.Tensor") -> "torch.Tensor":
            if self.training and self.noise_std > 0:
                return x + torch.randn_like(x) * self.noise_std
            return x

        def encode(self, x: "torch.Tensor") -> "torch.Tensor":
            return self.encoder(x)

        def decode(self, z: "torch.Tensor") -> "torch.Tensor":
            return self.decoder(z)

        def forward(self, x: "torch.Tensor") -> Tuple["torch.Tensor", "torch.Tensor"]:
            noisy = self.add_noise(x)
            z = self.encode(noisy)
            x_hat = self.decode(z)
            return x_hat, z

else:
    # Graceful fallback when PyTorch isn't installed
    class MusicAutoencoder:  # type: ignore[no-redef]
        def __init__(self, *args, **kwargs):
            raise ImportError(
                "PyTorch is required for the autoencoder. "
                "Install with: pip install torch"
            )


# ── Training Harness ─────────────────────────────────────────────────────────

class AutoencoderTrainer:
    """Train and use the MusicAutoencoder on a fitted ContentEngine.

    Parameters
    ----------
    latent_dim : int
        Dimensionality of the learned embedding space.
    noise_std : float
        Standard deviation of Gaussian noise added during training.
    lr : float
        Learning rate for Adam optimizer.
    epochs : int
        Number of training epochs.
    batch_size : int
        Mini-batch size.
    device : str
        'cpu', 'cuda', or 'mps'.
    """

    def __init__(
        self,
        latent_dim: int = 16,
        noise_std: float = 0.1,
        lr: float = 1e-3,
        epochs: int = 80,
        batch_size: int = 512,
        device: Optional[str] = None,
    ) -> None:
        if not _TORCH_AVAILABLE:
            raise ImportError("PyTorch is required. pip install torch")

        self.latent_dim = latent_dim
        self.noise_std = noise_std
        self.lr = lr
        self.epochs = epochs
        self.batch_size = batch_size

        if device is None:
            if torch.cuda.is_available():
                device = "cuda"
            elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                device = "mps"
            else:
                device = "cpu"
        self.device = torch.device(device)
        self.model: Optional[MusicAutoencoder] = None
        self._train_losses: list = []

    # ── Train ────────────────────────────────────────────────────────────

    def train(
        self,
        engine: ContentEngine,
        verbose: bool = True,
    ) -> "AutoencoderTrainer":
        """Train the autoencoder on the ContentEngine's scaled feature matrix."""
        engine._ensure_fitted()
        X = engine.X.astype(np.float32)
        input_dim = X.shape[1]

        self.model = MusicAutoencoder(
            input_dim=input_dim,
            latent_dim=self.latent_dim,
            noise_std=self.noise_std,
        ).to(self.device)

        dataset = TensorDataset(torch.from_numpy(X))
        loader = DataLoader(dataset, batch_size=self.batch_size, shuffle=True)

        optimizer = optim.Adam(self.model.parameters(), lr=self.lr)
        scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=self.epochs)
        criterion = nn.MSELoss()

        self.model.train()
        self._train_losses = []

        for epoch in range(1, self.epochs + 1):
            epoch_loss = 0.0
            for (batch,) in loader:
                batch = batch.to(self.device)
                x_hat, _ = self.model(batch)
                loss = criterion(x_hat, batch)
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                epoch_loss += loss.item() * len(batch)
            scheduler.step()

            avg_loss = epoch_loss / len(X)
            self._train_losses.append(avg_loss)

            if verbose and (epoch % 10 == 0 or epoch == 1):
                print(f"  Epoch {epoch:3d}/{self.epochs}  loss={avg_loss:.6f}")

        self.model.eval()
        return self

    # ── Encode ───────────────────────────────────────────────────────────

    def encode(self, X: np.ndarray) -> np.ndarray:
        """Encode scaled features → latent embeddings (numpy)."""
        if self.model is None:
            raise RuntimeError("Model not trained. Call train() first.")
        self.model.eval()
        with torch.no_grad():
            tensor = torch.from_numpy(X.astype(np.float32)).to(self.device)
            z = self.model.encode(tensor)
            return z.cpu().numpy()

    def encode_catalog(self, engine: ContentEngine) -> np.ndarray:
        """Encode the entire catalog from a fitted ContentEngine."""
        engine._ensure_fitted()
        return self.encode(engine.X)

    def encode_single(self, engine: ContentEngine, track_id: str) -> np.ndarray:
        """Encode a single track → 1-D latent vector."""
        vec = engine.get_track_vector(track_id).reshape(1, -1)
        return self.encode(vec)[0]

    # ── Reconstruction Quality ───────────────────────────────────────────

    def reconstruction_error(self, engine: ContentEngine) -> float:
        """Mean squared reconstruction error on the full catalog."""
        if self.model is None:
            raise RuntimeError("Model not trained.")
        engine._ensure_fitted()
        self.model.eval()
        with torch.no_grad():
            X_t = torch.from_numpy(engine.X.astype(np.float32)).to(self.device)
            x_hat, _ = self.model(X_t)
            mse = nn.functional.mse_loss(x_hat, X_t).item()
        return mse

    @property
    def train_losses(self) -> list:
        return list(self._train_losses)

    # ── Persistence ──────────────────────────────────────────────────────

    def save(self, path: str) -> None:
        """Save model weights to disk."""
        if self.model is None:
            raise RuntimeError("Nothing to save — model not trained.")
        torch.save({
            "state_dict": self.model.state_dict(),
            "config": {
                "input_dim": self.model.input_dim,
                "latent_dim": self.model.latent_dim,
                "noise_std": self.model.noise_std,
            },
            "train_losses": self._train_losses,
        }, path)
        print(f"Model saved → {path}")

    def load(self, path: str) -> "AutoencoderTrainer":
        """Load model weights from disk."""
        ckpt = torch.load(path, map_location=self.device, weights_only=False)
        cfg = ckpt["config"]
        self.model = MusicAutoencoder(**cfg).to(self.device)
        self.model.load_state_dict(ckpt["state_dict"])
        self.model.eval()
        self._train_losses = ckpt.get("train_losses", [])
        self.latent_dim = cfg["latent_dim"]
        return self

    # ── Repr ─────────────────────────────────────────────────────────────

    def __repr__(self) -> str:
        status = "trained" if self.model is not None else "untrained"
        return f"<AutoencoderTrainer({status}, latent={self.latent_dim}d, device={self.device})>"
