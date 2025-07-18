## Using `predict.py`to test the model

The following documentation outlines how to use the `predict.py` script in the `.drum_classifier/` module to test the outputs of a trained model

<!--date_created:mon-14-jul-2025-->
<!--date_updated:mon-14-jul-2025-->

-----

# `predict.py` - Multi-Label Drum Event Prediction (CNN Model)

This script is designed to perform multi-label drum event classification on audio files using your trained Convolutional Neural Network (CNN) model. It processes audio segments, identifies multiple drum types within each segment, and reports them with timestamps.

## Location

Based on your execution command `python3 drum_classifier/predict.py`, this script is located within the `drum_classifier` module:
`digital-performance-dashboard/drum_classifier/predict.py`

## Prerequisites

Before running `predict.py`, ensure you have:

1.  **Processed ENST Dataset:** You must have successfully run `process_enst_data.py` to generate the segmented audio files and the `multi_label_events.csv` metadata in `training_data/ENST_processed/`.
2.  **Trained Model:** You must have successfully run `model_trainer.py` to train the multi-label CNN model and save the following files in the `models/` directory:
      * `multi_label_drum_classifier_model.h5` (the Keras CNN model)
      * `multi_label_scaler.joblib` (the fitted `StandardScaler`)
      * `multi_label_label_map.json` (the mapping from drum names to numeric labels)

## Usage

Run `predict.py` from the root directory of your `DrumScript` project.

The script currently includes two example sections: one for a single 0.2-second segment and one for a longer audio file. You will need to uncomment and/or modify the `long_audio_filepath` variable to point to your desired audio file.

### Running the script

```bash
python3 drum_classifier/predict.py
```

### Modifying the Test Audio

Open `drum_classifier/predict.py` and look for the `if __name__ == "__main__":` block.
You'll see lines similar to these for specifying the audio files:

```python
    # --- Example 1: Predict single segment ---
    single_segment_audio_path = os.path.join(project_root, "training_data", "ENST_processed", "1_rock-prog_125_beat_4-4.wav")

    # --- Example 2: Process a longer audio file ---
    long_audio_filepath = os.path.join(project_root, "test_audio", "test.wav")
    # You can change this path to your specific WAV or MP3 file
    # Example: long_audio_filepath = os.path.join(project_root, "your_custom_audio", "my_song.mp3")
```

**To test with a specific WAV or MP3 file:**

1.  Locate the line `long_audio_filepath = os.path.join(project_root, "test_audio", "test.wav")`
2.  Change `"test.wav"` and/or `"test_audio"` to the actual path of your audio file. For instance, if your file is `my_song.mp3` directly in your `DrumScript/` project root, you might change it to:
    `long_audio_filepath = os.path.join(project_root, "my_song.mp3")`

## How it Works

The script performs the following steps:

1.  **Loads Components:** It loads the pre-trained Keras CNN model (`.h5`), the `StandardScaler` (`.joblib`), and the `label_map` (`.json`) from the `models/` directory.
2.  **Loads Audio:** For the "Longer Audio File Prediction Example," it loads the specified audio file (`long_audio_filepath`), resampling it to `SAMPLE_RATE` (22050 Hz) if necessary.
3.  **Segments Audio:** It divides the long audio file into 0.2-second segments (`SEGMENT_LENGTH_SECONDS`), using a `HOP_LENGTH_SECONDS` (default: 0.1 seconds) to create overlapping windows. This ensures comprehensive analysis.
4.  **Extracts Features:** For each segment, it computes 40 MFCC (Mel-frequency cepstral coefficients) features, which are then scaled using the loaded `StandardScaler`.
5.  **Predicts Drum Events:** The scaled MFCCs are fed into the CNN model, which outputs probabilities for each of the 6 drum types (`kick`, `snare`, `hi-hat`, `crash`, `ride`, `tom`).
6.  **Thresholding:** Any drum type with a probability above a hardcoded threshold (e.g., 0.5) is considered "present" in that segment.
7.  **Reports Results:** It prints a list of detected drum events, showing the approximate time (start of the segment) and the types of drums identified in that segment.

## Example Output (from your previous successful run)

```
Loading trained model, scaler, and label map...
WARNING:absl:Compiled the loaded model, but the compiled metrics have yet to be built. `model.compile_metrics` will be empty until you train or evaluate the model.
Model components loaded.

--- Single Segment Drum Prediction Example ---
Predicting drum types for single segment: /Users/victoriamckinney/Library/Visual Studio Projects/DrumScript/training_data/ENST_processed/1_rock-prog_125_beat_4-4.wav
Predicted drum types: ['hi-hat']

--- Longer Audio File Prediction Example ---
Processing long audio file: /Users/victoriamckinney/Library/Visual Studio Projects/DrumScript/test_audio/1_rock-prog_125_beat_4-4.wav
Segmenting & Predicting: 100%|██████████████████████████████████████████| 200/200 [00:00<00:00, 2000.00it/s]
--- Detected Drum Events (Time-stamped) ---
Time: 0.05s - Drums: kick
Time: 0.15s - Drums: hi-hat
# ... (and so on) ...
```

---

<!--END-->