import argparse
from pathlib import Path

import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np

def analyze_audio(input_path: Path, output_dir: Path) -> None:
	output_dir.mkdir(exist_ok=True)

	print(f"Loading: {input_path}")

	y, sr = librosa.load(input_path, sr=None, mono=True)

	duration = librosa.get_duration(y=y, sr=sr)
	print(f"Sample Rate: {sr}")
	print(f"Duration: {duration:.2f} seconds")

	tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
	beat_times = librosa.frames_to_time(beat_frames, sr=sr)
	
	tempo_value = float(np.asarray(tempo).item())
	
	print(f"Estimated tempo: {tempo_value:.2f} BPM")
	print(f"Detected beats: {len(beat_times)}")

	plot_waveform(y, sr, output_dir / "waveform.png")
	plot_spectrogram(y, sr, output_dir / "spectrogram.png")
	plot_chromagram(y, sr, output_dir / "chromagram.png")

	export_beats(beat_times, output_dir / "beats.csv")

	print(f"Save plots to: {output_dir}")

def plot_waveform(y, sr, output_path: Path) -> None:
    plt.figure(figsize=(12, 4))
    librosa.display.waveshow(y, sr=sr)
    plt.title("Waveform")
    plt.xlabel("Time")
    plt.ylabel("Amplitude")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

def plot_spectrogram(y, sr, output_path: Path) -> None:
	stft = librosa.stft(y)
	db = librosa.amplitude_to_db(np.abs(stft), ref=np.max)

	plt.figure(figsize=(12, 6))
	librosa.display.specshow(db, sr=sr, x_axis="time", y_axis="hz")
	plt.colorbar(format="%+2.0f dB")
	plt.title("Spectrogam")
	plt.tight_layout()
	plt.savefig(output_path)
	plt.close()

def plot_chromagram(y, sr, output_path: Path) -> None:
	chroma = librosa.feature.chroma_cqt(y=y, sr=sr)

	plt.figure(figsize=(12, 5))
	img = librosa.display.specshow(
		chroma,
		sr=sr,
		x_axis="time",
		y_axis="chroma"
	)
	plt.colorbar(img)
	plt.title("Chromagram")
	plt.tight_layout()
	plt.savefig(output_path)
	plt.close()
	
def export_beats(beat_times, output_path: Path) -> None:

	with output_path.open("w", encoding="utf-8") as f:
		f.write("beat_number,time_seconds\n")

		for index, beat_time in enumerate(beat_times, start=1):
			f.write(f"{index},{beat_time:.3f}\n")

def main() -> None:
	parser = argparse.ArgumentParser(
		description="Jeremy's Audio Microscope for music analysis"
		)
	parser.add_argument("input", help="Path to audio file")
	parser.add_argument(
		"--output",
		default="output",
		help="Directory where plots are to be saved",
		)

	args = parser.parse_args()

	analyze_audio(
		input_path=Path(args.input),
		output_dir=Path(args.output),
	)

if __name__ == "__main__":
	main()