"""WAV decoding helpers.

The frontend encodes recordings to 16-bit PCM mono WAV before upload, so the
backend needs no ffmpeg/system codecs to decode them.
"""

from __future__ import annotations

import io
import wave

import numpy as np


def load_wav(data: bytes) -> tuple[np.ndarray, int]:
    """Decode WAV bytes into a float32 mono signal in [-1, 1] and its sample rate."""
    with wave.open(io.BytesIO(data), "rb") as w:
        n_channels = w.getnchannels()
        sample_width = w.getsampwidth()
        sample_rate = w.getframerate()
        frames = w.readframes(w.getnframes())

    if sample_width == 2:
        x = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
    elif sample_width == 1:
        x = (np.frombuffer(frames, dtype=np.uint8).astype(np.float32) - 128.0) / 128.0
    elif sample_width == 4:
        x = np.frombuffer(frames, dtype=np.int32).astype(np.float32) / 2147483648.0
    else:
        raise ValueError(f"unsupported sample width: {sample_width} bytes")

    if n_channels > 1:
        x = x.reshape(-1, n_channels).mean(axis=1)
    return x, sample_rate


def rms(signal: np.ndarray) -> float:
    """Root-mean-square loudness of a signal."""
    if signal.size == 0:
        return 0.0
    return float(np.sqrt(np.mean(np.square(signal, dtype=np.float64))))


def has_speech(signal: np.ndarray, sample_rate: int, min_sec: float = 0.2, min_rms: float = 0.01) -> bool:
    """Crude voice-activity check: long enough and loud enough to be a real attempt."""
    duration = signal.size / sample_rate if sample_rate else 0.0
    return duration >= min_sec and rms(signal) > min_rms
