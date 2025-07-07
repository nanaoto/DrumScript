# **Creating your own training dataset**
## `DrumScript/data_labeller/data_labeller.py`
>
The following documentation outlines how you can use the `data_labeller/` module to **import your own drum audio** and **create a labelled dataset** Use cases for this might be:
>
* **Testing** `DrumScript` **core functionality**
* Submitting a **pull request** to `DrumScript` moderators
* **Testing a known issue** with the `DrumScript` package
* **Submitting a feature request** to `DrumScript` `base_model`
* Create a **bespoke** **`DrumScript` model**, for your **own personal use**.
  
<!-- date_created: mon-07-jul-2025-->

<!-- date_updated: mon-07-jul-2025-->

> **Updated functionality:**
> 
> For each detected drum event, the `data_labeler` module will now:
>
> 1. **Extract the audio segment.**
>
> 2. **Save this segment** as a `.wav` file in a new `audio_segments/` sub-folder within your chosen output directory (e.g., `labelled_datasets/audio_segments/`). 
> 3. **Include the path to this saved audio segment** in both the `JSON` and `CSV` output files under the field `"saved_audio_segment_path"`. 
> 
> **NOTE:** The filename will be descriptive, including the **original audio name**, **event number**, and **onset time** (e.g., groove_1_event_3_onset_2.15s.wav).
>
> These amendments allow for **easy post-review** and playback, post-script.


---

### How it Works

This module facilitates an **interactive labelling process**, which is the most effective way to accurately tag complex drum events like simultaneous hits or extremely fast patterns. 

**Here's a breakdown of the steps involved:**

1.  **Import Audio Files:** It takes a list of your drum audio recordings (MP3, WAV, etc.) as input.
2.  **Slice Files:** It uses DrumScript's existing `onset_detector` to identify individual drum hit events. For very fast passages, I've adjusted parameters to allow for more sensitive detection.
3.  **Interactive Playback & Labelling:** For *each* detected drum hit:
      * It plays a small audio segment of that specific event for you.
      * It prompts you to manually enter a label (e.g., `kick`, `snare`, `hi-hat`, `kick+snare`, `double_kick_right`, `double_kick_left`, etc.). This human input is vital for correctly identifying simultaneous drum hits or distinct, rapid events.
4.  **Feature Extraction:** For each labelled event, it extracts relevant audio features:
      * **Frequency (in Hz):** Represented by the `spectral_centroid_mean_hz`, which gives you the average "center of mass" of the frequencies in the sound, providing a good indicator of its brightness or pitch.
      * MFCCs (Mel-frequency Cepstral Coefficients): Standard features for distinguishing different sounds.
      * RMS (Root Mean Square) energy: A measure of loudness.
5.  **Labelled Output:** Once you've labelled all events in your files, the module saves the complete dataset in two formats:
      * **JSON file (`labelled_drum_dataset.json`):** Contains all event details, including raw and processed features.
      * **CSV file (`labelled_drum_dataset.csv`):** A flattened version of the data, suitable for direct use in machine learning model training.

---
### Setup and Running Instructions

1.  **Create the Module Directory:**

      * Navigate to your `DrumScript/` project root.
      * Create a new folder: `mkdir DrumScript/data_labeller`
      * Create an empty `__init__.py` file inside it: `touch DrumScript/data_labeller/__init__.py`
      * Place the code above into `DrumScript/data_labeller/data_labeller.py`.

2.  **Verify Imports:**

      * In the provided `data_labeller.py` code, ensure the import statements for `audio_loader`, `onset_detector`, and `feature_extractor` correctly reflect their location within your `DrumScript` package. I've used relative imports assuming they are correctly structured under `audio_processor`. If they are directly under `DrumScript`, adjust accordingly (e.g., `from .audio_loader import ...`). Based on your `repository_structure.md`, they should be `from DrumScript.audio_processor import ...`.

3.  **Install `sounddevice`:**

      * This library is crucial for playing the audio segments interactively.
      * Open your terminal in the `DrumScript` project root and run:
        ```bash
        uv pip install sounddevice
        ```
      * **Important for Audio Playback:** `sounddevice` relies on a system-level  library called **PortAudio**. You might need to install this separately:
          * **macOS:** `brew install portaudio` (if you have Homebrew)
          * **Ubuntu/Debian:** `sudo apt-get install libportaudio2`
          * **Windows:** PortAudio usually comes bundled with `sounddevice` wheels, or you might need to find specific installation instructions for your Python distribution.

4.  **Prepare Your Audio Files:**

      * Gather the MP3 or WAV files of your drum recordings that you want to label.
      * Update the `input_audio_paths` list in the `if __name__ == "__main__":` block of `data_labeller.py` with the actual paths to your files.

5.  **Run the Labeller:**

      * Open your terminal.
      * Navigate to your `DrumScript` project's root directory (the one containing `.venv`, `pyproject.toml`, etc.).
      * Execute the script using `uv run`:
        ```bash
        uv run python3 DrumScript/data_labeller/data_labeller.py
        ```

The script will then guide you through each drum event detected. Listen to the played segment carefully, and type in the appropriate label(s) (e.g., "kick", "snare+ride", "fast\_kick\_1", "fast\_kick\_2") and press Enter. Once finished, your `labelled_drum_dataset.json` and `labelled_drum_dataset.csv` files will be in the `labelled_datasets` folder.

---

### Updated instructions for using `data_labeller/` module:

You're right\! My apologies, it seems I missed including `librosa` and `soundfile` in the explicit installation instructions. These are crucial for the audio processing and saving functionalities.

Here's the corrected and enhanced `data_labeller.py` module, which now includes the functionality to **produce a small audio file for each event** and saves its path in the output data. I've also updated the instructions to ensure you have all the necessary libraries installed.

### Updated Functionality:

For each detected drum event, the module will now:

1.  **Extract the audio segment**.
2.  **Save this segment** as a `.wav` file in a new `audio_segments` sub-folder within your chosen output directory (e.g., `labelled_datasets/audio_segments/`). The filename will be descriptive, including the original audio name, event number, and onset time (e.g., `groove_1_event_3_onset_2.15s.wav`).
3.  **Include the path** to this saved audio segment in both the `JSON` and `CSV` output files under the field `"saved_audio_segment_path"`. This allows for easy post-review and playback.

### `DrumScript/data_labeller/data_labeller.py`

```python
import librosa
import numpy as np
import json
import csv
import os
from pathlib import Path
from typing import List, Dict, Any
import sounddevice as sd
import soundfile as sf
import time

# Import existing DrumScript modules
# Ensure these imports correctly reference your package structure
# For example, if audio_loader is in DrumScript/audio_processor/audio_loader.py
# from DrumScript.audio_processor import audio_loader
# from DrumScript.audio_processor import onset_detector
# from DrumScript.audio_processor import feature_extractor

# Assuming relative imports within the DrumScript package for demonstration
from audio_processor import audio_loader
from audio_processor import onset_detector
from audio_processor import feature_extractor


def play_audio_segment(y: np.ndarray, sr: int):
    """Plays an audio segment."""
    print("Playing segment...")
    try:
        sd.play(y, sr)
        sd.wait() # Wait until playback is finished
    except Exception as e:
        print(f"Error playing audio segment: {e}. Make sure sounddevice is configured correctly.")
        print("You might need to install portaudio: `brew install portaudio` (macOS), `sudo apt-get install libportaudio2` (Ubuntu/Debian) or similar for your OS.")

def extract_features_for_segment(y_segment: np.ndarray, sr: int) -> Dict[str, Any]:
    """
    Extracts relevant features for a given audio segment.
    Includes spectral centroid as a 'frequency' representative.
    """
    features = {}
    if len(y_segment) > 0:
        # MFCCs (commonly used for drum classification)
        # Using a fixed n_mfcc=13, which is common
        mfccs = librosa.feature.mfcc(y=y_segment, sr=sr, n_mfcc=13)
        features['mfccs_mean'] = mfccs.mean(axis=1).tolist() if mfccs.size > 0 else [0.0]*13
        features['mfccs_std'] = mfccs.std(axis=1).tolist() if mfccs.size > 0 else [0.0]*13

        # Spectral Centroid (a good indicator of 'brightness' or average frequency)
        # Add a small epsilon to prevent division by zero for very quiet segments
        spectral_centroids = librosa.feature.spectral_centroid(y=y_segment + 1e-6, sr=sr)
        features['spectral_centroid_mean_hz'] = float(spectral_centroids.mean()) if spectral_centroids.size > 0 else 0.0
        features['spectral_centroid_std_hz'] = float(spectral_centroids.std()) if spectral_centroids.size > 0 else 0.0

        # Root Mean Square (RMS) energy (loudness)
        rms = librosa.feature.rms(y=y_segment)
        features['rms_mean'] = float(rms.mean()) if rms.size > 0 else 0.0
        features['rms_std'] = float(rms.std()) if rms.size > 0 else 0.0

    return features

def process_and_label_audio(
    audio_filepath: Path,
    output_dir: Path, # Directory to save labelled data and audio segments
    onset_offset_ms: int = 50, # Time before onset to start segment
    onset_duration_ms: int = 200, # Duration after onset for segment
    onset_pre_max: int = 1, # Parameters for librosa onset detection
    onset_post_max: int = 1,
    onset_pre_avg: int = 1,
    onset_post_avg: int = 1,
    onset_wait: int = 1,
    onset_delta: float = 0.03, # Lower delta can make it more sensitive to small peaks (e.g., fast double bass)
    onset_backtrack: bool = False # Set to False for very fast, distinct hits to avoid merging
) -> List[Dict[str, Any]]:
    """
    Loads an audio file, detects onsets, and interactively prompts the user
    to label each detected drum event. It also saves each segment to an audio file.
    """
    print(f"\n--- Processing '{audio_filepath.name}' for labelling ---")
    y, sr = audio_loader.load_audio(str(audio_filepath))
    y = audio_loader.normalize_audio(y)

    # Create a subdirectory for audio segments within the main output_dir
    audio_segments_output_path = output_dir / "audio_segments"
    audio_segments_output_path.mkdir(parents=True, exist_ok=True)

    # Use existing onset detection logic, potentially with refined parameters
    onset_frames = onset_detector.detect_onsets(
        y=y, sr=sr,
        pre_max=onset_pre_max, post_max=onset_post_max,
        pre_avg=onset_pre_avg, post_avg=onset_post_avg,
        wait=onset_wait, delta=onset_delta, backtrack=onset_backtrack
    )

    onset_times = librosa.frames_to_time(onset_frames, sr=sr)
    print(f"Detected {len(onset_times)} onsets in '{audio_filepath.name}'.")

    labelled_events = []
    for i, onset_time in enumerate(onset_times):
        # Define segment boundaries
        start_time = max(0, onset_time - (onset_offset_ms / 1000.0))
        end_time = min(librosa.get_duration(y=y, sr=sr), onset_time + (onset_duration_ms / 1000.0))

        # Convert times to sample indices
        start_sample = int(start_time * sr)
        end_sample = int(end_time * sr)

        # Extract audio segment
        y_segment = y[start_sample:end_sample]

        # Save the audio segment to a file
        segment_filename = f"{audio_filepath.stem}_event_{i+1}_onset_{onset_time:.2f}s.wav"
        segment_filepath = audio_segments_output_path / segment_filename
        
        try:
            sf.write(str(segment_filepath), y_segment, sr)
            print(f"Saved segment to: {segment_filepath}")
        except Exception as e:
            print(f"Error saving audio segment {segment_filepath}: {e}")
            segment_filepath = None # Mark as failed if saving fails

        print(f"\n--- Event {i+1}/{len(onset_times)} at {onset_time:.2f}s ---")
        play_audio_segment(y_segment, sr)

        # Extract features for the segment
        segment_features = extract_features_for_segment(y_segment, sr)

        # Prompt for user label
        label = input("Enter label(s) for this drum event (e.g., kick, snare, kick+snare): ").strip()
        while not label:
            print("Label cannot be empty. Please provide a label.")
            label = input("Enter label(s) for this drum event (e.g., kick, snare, kick+snare): ").strip()

        event_data = {
            "audio_filename": audio_filepath.name,
            "onset_time_s": float(onset_time),
            "segment_start_s": float(start_time),
            "segment_end_s": float(end_time),
            "segment_duration_s": float(end_time - start_time),
            "label": label,
            "saved_audio_segment_path": str(segment_filepath) if segment_filepath else None,
            "features": segment_features
        }
        labelled_events.append(event_data)

    print(f"Finished processing '{audio_filepath.name}'.")
    return labelled_events

def generate_labelled_dataset(audio_file_paths: List[str], output_dir: str):
    """
    Main function to generate a labelled dataset from multiple audio files.

    Args:
        audio_file_paths (List[str]): List of paths to input audio files.
        output_dir (str): Directory to save the JSON and CSV output files,
                          and a subdirectory for audio segments.
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    all_labelled_events = []

    for file_path_str in audio_file_paths:
        file_path = Path(file_path_str)
        if not file_path.exists():
            print(f"Warning: Audio file not found: {file_path_str}. Skipping.")
            continue
        if not file_path.suffix.lower() in ['.mp3', '.wav', '.flac', '.ogg']:
            print(f"Warning: Unsupported audio format for {file_path_str}. Skipping.")
            continue

        labelled_events_for_file = process_and_label_audio(file_path, output_path)
        all_labelled_events.extend(labelled_events_for_file)

    if not all_labelled_events:
        print("No events were labelled. No output files generated.")
        return

    # Save to JSON
    json_output_filepath = output_path / "labelled_drum_dataset.json"
    with open(json_output_filepath, 'w') as f:
        json.dump(all_labelled_events, f, indent=4)
    print(f"\nLabelled dataset saved to: {json_output_filepath}")

    # Save to CSV
    csv_output_filepath = output_path / "labelled_drum_dataset.csv"
    if all_labelled_events:
        csv_data = []
        # Dynamically build feature headers based on actual extracted features
        mfcc_mean_headers = [f"mfccs_mean_{i}" for i in range(13)]
        mfcc_std_headers = [f"mfccs_std_{i}" for i in range(13)]
        
        feature_specific_headers = [
            "spectral_centroid_mean_hz", "spectral_centroid_std_hz",
            "rms_mean", "rms_std"
        ]
        
        base_headers = [
            "audio_filename", "onset_time_s", "segment_start_s",
            "segment_end_s", "segment_duration_s", "label",
            "saved_audio_segment_path" # Added this field
        ]
        
        all_headers = base_headers + mfcc_mean_headers + mfcc_std_headers + feature_specific_headers

        for event in all_labelled_events:
            row = {
                "audio_filename": event["audio_filename"],
                "onset_time_s": event["onset_time_s"],
                "segment_start_s": event["segment_start_s"],
                "segment_end_s": event["segment_end_s"],
                "segment_duration_s": event["segment_duration_s"],
                "label": event["label"],
                "saved_audio_segment_path": event["saved_audio_segment_path"] # Added this field
            }
            # Flatten MFCCs and other features
            features_dict = event.get("features", {})
            for i, val in enumerate(features_dict.get("mfccs_mean", [])):
                row[f"mfccs_mean_{i}"] = val
            for i, val in enumerate(features_dict.get("mfccs_std", [])):
                row[f"mfccs_std_{i}"] = val
            
            row["spectral_centroid_mean_hz"] = features_dict.get("spectral_centroid_mean_hz")
            row["spectral_centroid_std_hz"] = features_dict.get("spectral_centroid_std_hz")
            row["rms_mean"] = features_dict.get("rms_mean")
            row["rms_std"] = features_dict.get("rms_std")
            
            csv_data.append(row)

        with open(csv_output_filepath, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=all_headers)
            writer.writeheader()
            writer.writerows(csv_data)
        print(f"Labelled dataset saved to: {csv_output_filepath}")

if __name__ == "__main__":
    # --- IMPORTANT: Replace with your actual paths for testing ---
    # Create example_recordings directory and put your .mp3 or .wav files there.
    # For initial testing, you can use the provided test.mp3:
    # "test_audio/reference_audio/test.mp3"
    
    # Example usage:
    input_audio_paths = [
        "test_audio/reference_audio/test.mp3", # Example from your repo
        # "path/to/your/groove_1.wav",
        # "path/to/your/double_bass_run.mp3",
        # Add as many audio files as you want to label
    ]

    output_dataset_dir = "labelled_datasets" # This directory will be created

    print("Starting labelled dataset generation...")
    generate_labelled_dataset(input_audio_paths, output_dataset_dir)
    print("Labelled dataset generation complete.")
```

### Updated Setup and Running Instructions:

To get this new functionality working, please follow these steps carefully, paying special attention to the library installations:

1.  **Create the Module Directory:**

      * Navigate to your `DrumScript/` project root.
      * Create a new folder: `mkdir DrumScript/data_labeller`
      * Create an empty `__init__.py` file inside it: `touch DrumScript/data_labeller/__init__.py`
      * Place the code above into `DrumScript/data_labeller/data_labeller.py`.

2.  **Verify Imports:**

      * In the provided `data_labeller.py` code, ensure the import statements for `audio_loader`, `onset_detector`, and `feature_extractor` correctly reflect their location within your `DrumScript` package. I've used relative imports assuming they are correctly structured under `audio_processor`. Based on your `repository_structure.md`, they should be `from DrumScript.audio_processor import ...`.

3.  **Install Essential Libraries:**

      * You need `librosa`, `soundfile`, and `sounddevice` for the module to function correctly.
      * Open your terminal in the `DrumScript` project root and run these commands:
        ```bash
        uv pip install librosa
        uv pip install soundfile
        uv pip install sounddevice
        ```
      * **Important for Audio Playback (`sounddevice`):** `sounddevice` relies on a system-level library called **PortAudio**. You might need to install this separately:
          * **macOS:** `brew install portaudio` (if you have Homebrew)
          * **Ubuntu/Debian:** `sudo apt-get install libportaudio2`
          * **Windows:** PortAudio usually comes bundled with `sounddevice` wheels, or you might need to find specific installation instructions for your Python distribution.

4.  **Prepare Your Audio Files:**

      * Gather the MP3 or WAV files of your drum recordings that you want to label.
      * Update the `input_audio_paths` list in the `if __name__ == "__main__":` block of `data_labeller.py` with the actual paths to your files.

5.  **Run the Labeller:**

      * Open your terminal.
      * Navigate to your `DrumScript` project's root directory (the one containing `.venv`, `pyproject.toml`, etc.).
      * Execute the script using `uv run`:
        ```bash
        uv run python3 DrumScript/data_labeller/data_labeller.py
        ```

The script will then guide you through each drum event detected. Listen to the played segment carefully, and type in the appropriate label(s) (e.g., "kick", "snare+ride", "fast\_kick\_1", "fast\_kick\_2") and press Enter. Once finished, your `labelled_drum_dataset.json` and `labelled_drum_dataset.csv` files will be in the `labelled_datasets` folder, and a new `labelled_datasets/audio_segments` folder will contain all the individual audio clips.
<!--END-->