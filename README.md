# amscope
Audio Microscope - a sonic analysis proggram for properly digging structure from sound

# About amscope

`amscope` is a small Python audio microscope. It takes an audio file, looks at basic musical and acoustic features, and saves images that help us see what is happening inside the sound.

## What happens when the script runs

When you run:

```bash
python amscope.py [FILE]
```

`amscope` does these steps:

1. Read command-line arguments.
2. Load an audio file.
3. Print sample rate and duration.
4. Estimate tempo and beat positions.
5. Save a waveform image.
6. Save a spectrogram image.
7. Save a chromagram image.

## 1. Read command-line arguments

The script uses `argparse` to read information from the command line.

For example:

```bash
python amscope.py samples/test.wav
```

Here `samples/test.wav` is the input file. The script also allows an optional output folder, but if none is provided, it uses `output/` by default.

## 2. Load an audio file

This also uses `librosa` to load the audio file.

The important line creates two values:

```python
y, sr = librosa.load(input_path, sr=None, mono=True)
```

`y` is the audio signal itself. It is the sound data represented as a NumPy array.

`sr` is the sample rate. For example, `44100` means the audio has 44,100 samples per second.

A useful beginner mental model:

```text
y = the sound
sr = how fast the sound is sampled
```

## 3. Print sample rate and duration

After the file is loaded, the script prints basic information about it.

The sample rate tells us how many audio samples happen each second.

The duration tells us how long the recording is.

This confirms that the file loaded correctly before we try deeper analysis.

## 4. Estimate tempo and beat positions

The script asks `librosa` to estimate the tempo and detect beats.

Tempo is reported in BPM, or beats per minute.

Beat positions tell us where the program thinks the musical pulse happens over time.

This is only an estimate. Some recordings are easier to analyze than others, especially if the rhythm is clear and steady.

## 5. Save a waveform image

The waveform shows amplitude over time.

It helps answer:

```text
How loud is the sound at each moment?
```

This is useful for seeing silence, loud sections, attacks, fades, and the general shape of the recording.

## 6. Save a spectrogram image

The spectrogram shows frequency content over time.

It helps answer:

```text
Which frequencies are present, and when?
```

Low sounds, high sounds, bright sounds, dense sounds, and changing textures can show up visually in a spectrogram.

## 7. Save a chromagram image

The chromagram shows musical pitch-class energy over time.

Instead of showing every exact frequency, it groups sound into the twelve pitch classes:

```text
C, C#, D, D#, E, F, F#, G, G#, A, A#, B
```

It helps answer:

```text
Which musical notes or pitch areas are active over time?
```

This will be useful later for exploring key detection, chord detection, and harmonic movement.

## Current output

After a successful run, the `output/` folder should contain images like:

```text
waveform.png
spectrogram.png
chromagram.png
```

These images are the first version of the audio microscope.

The current version is simple on purpose. It gives us a working foundation.

Future features:

- writing beat timestamps to a text file
- adding measure or bar markers
- estimating key centers
- making rough chord guesses
- exporting a simple chord chart

For now, the important win is this:

```text
The script can load sound, analyze it, and show us useful pictures of what is happening inside the recording.
```

