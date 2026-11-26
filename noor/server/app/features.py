"""MFCC feature extraction implemented with NumPy only (no librosa/scipy).

MFCCs capture the spectral envelope of speech and are a standard, lightweight
representation for comparing how two utterances were articulated.
"""

from __future__ import annotations

import numpy as np


def _hz_to_mel(hz: np.ndarray | float) -> np.ndarray | float:
    return 2595.0 * np.log10(1.0 + np.asarray(hz) / 700.0)


def _mel_to_hz(mel: np.ndarray | float) -> np.ndarray | float:
    return 700.0 * (10.0 ** (np.asarray(mel) / 2595.0) - 1.0)


def _mel_filterbank(n_filters: int, nfft: int, sr: int) -> np.ndarray:
    mel_min = _hz_to_mel(0.0)
    mel_max = _hz_to_mel(sr / 2.0)
    mel_points = np.linspace(mel_min, mel_max, n_filters + 2)
    hz_points = _mel_to_hz(mel_points)
    bins = np.floor((nfft + 1) * hz_points / sr).astype(int)
    bins = np.clip(bins, 0, nfft // 2)

    fb = np.zeros((n_filters, nfft // 2 + 1))
    for m in range(1, n_filters + 1):
        left, center, right = bins[m - 1], bins[m], bins[m + 1]
        center = max(center, left + 1)
        right = max(right, center + 1)
        for k in range(left, center):
            fb[m - 1, k] = (k - left) / (center - left)
        for k in range(center, min(right, nfft // 2 + 1)):
            fb[m - 1, k] = (right - k) / (right - center)
    return fb


def _dct2(x: np.ndarray) -> np.ndarray:
    """Orthonormal DCT-II along the last axis."""
    n_features = x.shape[1]
    n = np.arange(n_features)
    k = n.reshape(-1, 1)
    basis = np.cos(np.pi * (2 * n + 1) * k / (2 * n_features))
    y = x @ basis.T
    y *= np.sqrt(2.0 / n_features)
    y[:, 0] *= 1.0 / np.sqrt(2.0)
    return y


def mfcc(
    signal: np.ndarray,
    sr: int,
    n_mfcc: int = 13,
    n_filters: int = 26,
    frame_ms: float = 25.0,
    hop_ms: float = 10.0,
    nfft: int = 512,
    preemph: float = 0.97,
) -> np.ndarray:
    """Return an (n_frames, n_mfcc) MFCC matrix with cepstral mean normalization."""
    signal = np.asarray(signal, dtype=np.float64)
    if signal.size == 0:
        return np.zeros((0, n_mfcc))

    emphasized = np.append(signal[0], signal[1:] - preemph * signal[:-1])
    frame_len = int(round(sr * frame_ms / 1000.0))
    hop = max(1, int(round(sr * hop_ms / 1000.0)))
    if len(emphasized) < frame_len:
        emphasized = np.pad(emphasized, (0, frame_len - len(emphasized)))

    n_frames = 1 + (len(emphasized) - frame_len) // hop
    offsets = np.arange(0, n_frames * hop, hop)[:, None]
    indices = offsets + np.arange(frame_len)[None, :]
    frames = emphasized[indices] * np.hamming(frame_len)

    spectrum = np.abs(np.fft.rfft(frames, nfft))
    power = (spectrum ** 2) / nfft
    fb = _mel_filterbank(n_filters, nfft, sr)
    energies = power @ fb.T
    energies = np.where(energies == 0.0, np.finfo(float).eps, energies)
    feats = _dct2(np.log(energies))[:, :n_mfcc]
    feats -= feats.mean(axis=0, keepdims=True)
    return feats
