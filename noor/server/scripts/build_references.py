"""Build reference MFCC files from a folder of reference recordings.

Record a qualified reciter (قارئ) saying each letter with each harakah, save the
WAV files named:  {letter}__{harakah}__{index}.wav
(e.g. ta2__fatha__1.wav), then run:

    python -m scripts.build_references --in ./raw_audio --out ./references

The resulting .npy MFCC files are what ReferenceDtwAssessor compares against.
Letter/harakah ids must match the frontend curriculum (src/data/curriculum.ts).
"""

from __future__ import annotations

import argparse
import glob
import os

import numpy as np

from app.audio import load_wav
from app.features import mfcc


def main() -> None:
    parser = argparse.ArgumentParser(description="Build MFCC reference files from WAV recordings.")
    parser.add_argument("--in", dest="in_dir", required=True, help="folder with {letter}__{harakah}__{idx}.wav files")
    parser.add_argument("--out", dest="out_dir", required=True, help="output folder for .npy reference features")
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    wavs = sorted(glob.glob(os.path.join(args.in_dir, "*__*__*.wav")))
    if not wavs:
        print(f"No files matching '*__*__*.wav' in {args.in_dir}")
        return

    count = 0
    for path in wavs:
        stem = os.path.basename(path)[: -len(".wav")]
        with open(path, "rb") as f:
            signal, sr = load_wav(f.read())
        feats = mfcc(signal, sr)
        np.save(os.path.join(args.out_dir, f"{stem}.npy"), feats)
        count += 1
    print(f"Wrote {count} reference feature file(s) to {args.out_dir}")


if __name__ == "__main__":
    main()
