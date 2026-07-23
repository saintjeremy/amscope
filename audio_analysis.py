## Audio interpretation and preview generation.

## This module works with audio signals. It returns ordinary Python dictionaries
## and leaves decisions about where JSON belongs to ``library_store``.


from pathlib import Path
from typing import Any, Dict

import librosa
import librosa.display
import matplotlib

## A non-interactive backend works in terminals and future background workers.

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np


SCHEMA_VERSION = 1
PITCH_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def analyze_audio(input_path: Path, previews_dir: Path) -> Dict[str, Any]:
    ## Analyze an audio file and return serializable summary and beat data.
    print(f"Loading: {input_path}")
    y, sample_rate = librosa.load(input_path, sr=None, mono=True)
    duration = float(librosa.get_duration(y=y, sr=sample_rate))
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sample_rate)

    # Librosa versions return tempo as either a scalar or one-value array.
    tempo_bpm = float(np.asarray(tempo).reshape(-1)[0])
    beat_times = librosa.frames_to_time(beat_frames, sr=sample_rate)
    chroma = librosa.feature.chroma_cqt(y=y, sr=sample_rate)

    summary = {
        "schemaVersion": SCHEMA_VERSION,
        "durationSeconds": round(duration, 6),
        "sampleRateHz": int(sample_rate),
        "tempoBpm": round(tempo_bpm, 3),
        "detectedBeatCount": int(len(beat_times)),
        "chromaMean": {
            pitch: round(float(value), 6)
            for pitch, value in zip(PITCH_NAMES, np.mean(chroma, axis=1))
        },
    }
    beats = {
        "schemaVersion": SCHEMA_VERSION,
        "unit": "seconds",
        "times": [round(float(value), 6) for value in beat_times],
    }

    previews_dir.mkdir(parents=True, exist_ok=True)
    plot_waveform(y, sample_rate, previews_dir / "waveform.png")
    plot_spectrogram(y, sample_rate, previews_dir / "spectrogram.png")
    plot_chromagram(chroma, sample_rate, previews_dir / "chromagram.png")

    print(f"Duration: {duration:.2f} seconds")
    print(f"Estimated tempo: {tempo_bpm:.2f} BPM")
    print(f"Detected beats: {len(beat_times)}")
    return {"summary": summary, "beats": beats}


def plot_waveform(y: np.ndarray, sample_rate: int, output_path: Path) -> None:
    #Draw signal amplitude over time.
    fig, axis = plt.subplots(figsize=(12, 4))
    librosa.display.waveshow(y, sr=sample_rate, ax=axis)
    axis.set(title="Waveform")
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def plot_spectrogram(y: np.ndarray, sample_rate: int, output_path: Path) -> None:
    ## Draw the strength of frequencies over time.
    db = librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=np.max)
    fig, axis = plt.subplots(figsize=(12, 6))
    image = librosa.display.specshow(
        db, sr=sample_rate, x_axis="time", y_axis="log", ax=axis
    )
    fig.colorbar(image, ax=axis, format="%+2.0f dB")
    axis.set(title="Spectrogram")
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def plot_chromagram(chroma: np.ndarray, sample_rate: int, output_path: Path) -> None:
    ## Draw the relative presence of the twelve pitch classes over time.
    fig, axis = plt.subplots(figsize=(12, 5))
    image = librosa.display.specshow(
        chroma, sr=sample_rate, x_axis="time", y_axis="chroma", ax=axis
    )
    fig.colorbar(image, ax=axis)
    axis.set(title="Chromagram")
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)