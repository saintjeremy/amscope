## Librosa mental model

- `y` is the audio signal as a NumPy array.
- `sr` is sample rate.
- Most analysis functions take `y` and `sr`.
- Many visualizations need a feature matrix, not raw audio.
- `specshow()` draws a feature matrix as an image.
- `colorbar()` needs the image object returned by `specshow()`.