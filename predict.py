import os
import librosa
import numpy as np
import joblib
import json

# Corrected imports for predict.py located in the project root
from drum_classifier.drum_model import DrumClassifier
from audio_processor.feature_extractor import extract_features
from audio_processor.onset_detector import detect_onsets

def run_prediction(audio_path):
    """
    Loads the trained model, scaler, and label map,
    then processes an audio file to classify drum sounds.
    """
    # Paths are now directly relative to the project root
    # (where predict.py is located)
    models_dir = os.path.join(os.path.dirname(__file__), 'models')
    model_path = os.path.join(models_dir, 'drum_classifier_model.joblib')
    scaler_path = os.path.join(models_dir, 'scaler.joblib')
    label_map_path = os.path.join(models_dir, 'label_map.json')

    print(f"Loading model from: {model_path}")
    print(f"Loading scaler from: {scaler_path}")
    print(f"Loading label map from: {label_map_path}")

    try:
        # Load the trained model
        drum_classifier = DrumClassifier(model_type='random_forest') # Specify the model type used during training
        drum_classifier.model = joblib.load(model_path)

        # Load the scaler
        scaler = joblib.load(scaler_path)

        # Load the label map
        with open(label_map_path, 'r') as f:
            label_map = json.load(f)
        # Invert the label map for predictions (numeric to string)
        inverse_label_map = {v: k for k, v in label_map.items()}

        print(f"\nProcessing audio file: {audio_path}")
        
        # Diagnostic lines
        print(f"DEBUG: Attempting to load path: {audio_path}")
        print(f"DEBUG: os.path.exists check: {os.path.exists(audio_path)}")
        # End Diagnosis

        y, sr = librosa.load(audio_path, sr=None)

        # Apply onset detection
        onset_frames = detect_onsets(y, sr)
        onset_samples = librosa.frames_to_samples(onset_frames)

        if len(onset_samples) == 0:
            print("No onsets detected in the audio file.")
            return

        print(f"Detected {len(onset_samples)} onsets. Extracting features...")

        all_features = []
        for i, onset_sample in enumerate(onset_samples):
            # Define the segment around the onset (e.g., 2048 samples)
            # Ensure the segment does not go out of bounds
            start_sample = max(0, onset_sample - 1024)
            end_sample = min(start_sample + 2048, len(y))

            segment = y[start_sample:end_sample]
            
            if len(segment) > 0:
                features = extract_features(segment, sr)
                
                # --- NEW FIX: Flatten features if they are a dictionary ---
                if isinstance(features, dict):
                    print("DEBUG: Feature extractor returned a dictionary. Attempting to flatten it.")
                    flattened_features = []
                    # Iterate through sorted keys to ensure consistent feature order
                    for key in sorted(features.keys()):
                        value = features[key]
                        if isinstance(value, (np.ndarray, list)):
                            # Extend with flattened values
                            flattened_features.extend(np.array(value).flatten().tolist())
                        elif isinstance(value, (int, float)):
                            # Append scalar values directly
                            flattened_features.append(value)
                        else:
                            print(f"WARNING: Unhandled feature type in dictionary: {type(value)} for key {key}")
                    features = np.array(flattened_features)
                # --- END NEW FIX ---
                
                all_features.append(features)

        if not all_features:
            print("No features extracted from detected onsets.")
            return

        X_new = np.array(all_features)

        # Scale the new features using the loaded scaler
        X_new_scaled = scaler.transform(X_new)

        # Predict the drum type
        predictions_numeric = drum_classifier.predict(X_new_scaled)

        print("\n--- Classification Results ---")
        for i, pred_numeric in enumerate(predictions_numeric):
            predicted_label = inverse_label_map.get(pred_numeric, f"Unknown Label {pred_numeric}")
            onset_time = librosa.samples_to_time(onset_samples[i], sr=sr)
            print(f"Onset at {onset_time:.2f}s: Predicted as '{predicted_label}'")

    except FileNotFoundError as e:
        print(f"Error: Required file not found - {e}. Make sure 'models/' directory and specified files exist.")
        print("Please ensure your 'models/' directory contains 'drum_classifier_model.joblib', 'scaler.joblib', and 'label_map.json'.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    # Paths are now directly relative to the script's location (project root)
    test_audio_file = os.path.join(os.path.dirname(__file__), 'test_audio', 'reference_audio', 'test.mp3')
    
    if not os.path.exists(test_audio_file):
        print(f"Error: Test audio file not found at '{test_audio_file}'.")
        print("Please place your MP3 drum sound file (e.g., 'test.mp3') inside the 'DrumScript/test_audio/reference_audio/' directory.")
    else:
        run_prediction(test_audio_file)